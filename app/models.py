# -*- coding: utf-8 -*-
from . import db,login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,request
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin,AnonymousUserMixin#!!
from datetime import datetime
import hashlib
from markdown import markdown
import bleach


#保证数据库的安全，存储密码的散列值，核对密码时比较的是散列值，计算散列函数可复现
#生成散列值无法还原原来的密码

class Permission:#权限常量
    FOLLOW=0x01
    COMMENT=0x02
    WRITE_ARTICLES=0x04
    MODERATE_COMMENTS=0x08
    ADMINISTER=0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    default=db.Column(db.Boolean,default=True,index=False)#default默认字段，角色设为默认值
    permissions=db.Column(db.Integer)#整数，位标志

    @staticmethod
    def insert_roles():#数据库中创建角色
        roles={  #每个角色的权限，User是默认角色
            'User':(Permission.FOLLOW|
                     Permission.COMMENT|
                     Permission.WRITE_ARTICLES,True),#！！逗号不能忘！！
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT|
                          Permission.WRITE_ARTICLES|
                          Permission.MODERATE_COMMENTS,True),
            'Administer':(0xff,False)
        }

        for r in roles:#若角色名name是r在数据库中
            role=Role.query.filter_by(name=r).first()#查找现有角色
            if role is None:#角色名不存在
                role=Role(name=r)#加入数据库
            role.permissions=roles[r][0]#修改权限
            role.default=roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class Post(db.Model):
    __tablename__='posts'
    id=db.Column(db.Integer,primary_key=True)
    title = db.Column(db.Text)
    body=db.Column(db.Text)
    timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)#时间戳
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))#作者ip
    body_html=db.Column(db.Text)

    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py

        seed()#python标准库里内置的随机数种子
               #认为是系统提供的一个接口，一般随机数都是一个伪随机数，使用种子之后，能在概率上产生近似的随机数值
               #伪随机数的生成一般依赖于对每个初始值做操作，这里的某个初始值一般是由生成器生成的，这个初始值一般会根据当前时间产生，
               #所以你在不同的时间调用，产生的值是不同的，如果你使用相同的种子，则产生的随机数是相同的。
        user_count=User.query.count()
        for i in range(count):
            u=User.query.offset(randint(0,user_count-1)).first()#offset偏移原查询结果，返回一个新查询，跳过参数中指定的记录数量
            p=Post(body=forgery_py.lorem_ipsum.sentences(randint(1,3)),
                   timestamp=forgery_py.date.date(True),
                   author=u)#简介
            db.session.add(p)
            db.session.commit()

    @staticmethod#Post模型中处理markdown文本
    def on_changed_body(target,value,oldvalue,initiator):#将body字段文本渲染成html格式，结果保存在body_html中
        allowed_tags=['a','abbr','acronym','b','blockquote','code','em','i','li','ol','pre','strong','ul','h1','h2','h3','p']#允许的标签
        target.body_html=bleach.linkify(bleach.clean(#clean()删除所有不在白名单的标签   linkify()将纯文本中的url转换成适当的<a>链接
            markdown(value,output_format='html'),#markdowm函数将markdown文本转换html格式
            tags=allowed_tags,strip=True))#允许的标签

db.event.listen(Post.body,'set',Post.on_changed_body)#函数注册在body字段上，是SQLAlchemy "set"事件的监听程序
                                                         #body字段设置新值，函数自动调用


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed=db.Column(db.Boolean,default=False)
    name=db.Column(db.String(64))#真实姓名
    location=db.Column(db.String(64))#所在地
    about_me=db.Column(db.Text())#自我介绍
    member_since=db.Column(db.DateTime(),default=datetime.utcnow)#注册日期
    last_seen=db.Column(db.DateTime(),default=datetime.utcnow)#最后访问日期
    avatar_hash=db.Column(db.String(32))
    posts=db.relationship('Post',backref='author',lazy='dynamic')


    def __init__(self,**kwargs):#定义默认角色是用户，是构造函数
        super(User,self).__init__(**kwargs)#调用基类的构造函数
        if self.role is None:#若基类对象没有定义对象
            if self.email==current_app.config['FLASKY_ADMIN']:#如果基类对象的email和当前程序的环境变量相同时
                self.role=Role.query.filter_by(permissions=0xff).first()#将权限是0xff的角色赋给基类对象
            if self.role is None:
                self.role=Role.query.filter_by(default=True).first()#默认角色赋给基类对象
            if self.email is not None and self.avatar_hash is None:#email不存在和散列值不存在
                self.avatar_hash=hashlib.md5(self.email.encode('utf-8')).hexdigest()#生成md5 hash

    def ping(self):#刷新用户的最后访问时间
        self.last_seen=datetime.utcnow()
        db.session.add(self)


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)#以原始密码为输入，以字符串形式返回密码的散列值，保存在数据库中
                            #generate_password_hash(password,method=pbkdf2:sha2,salt_length=8)
    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)#参数数据库中取出的密码散列值，和用户输入的密码

                                                                #check_password_hash(hash,password)
    def generate_confirmation_token(self,expiration=3600):
        s=Serializer(current_app.config['SECRET_KEY'])#生成具有过期时间的JONS Web 签名
        return s.dumps({'confirm':self.id})#dumps（）为指定的数据生成加密签名，将数据和签名序列化，生成令牌字符串

    def confirm(self,token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)#为了解码令牌，检验签名和过期时间，不正确抛出异常
        except:
            return False
        if data.get('confirm')!=self.id:#检验令牌中的id和存储在current_user中的已登陆的用户匹配
            return False
        self.confirmed=True
        db.session.add(self)#如果检验通过，将添加的confirmed属性设为true
        return True

    def generate_reset_token(self,expiration=3600):
        s=Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'reset':self.id})

    def reset_password(self,token,new_password):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)#为了解码令牌，检验签名和过期时间
        except:
            return False
        if data.get('reset')!=self.id:
            return False
        self.password=new_password#修改密码
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash=hashlib.md5(self.email.encode('utf-8')).hexdigest()#email改变，散列值也改变
        db.session.add(self)
        return True

    def can(self,permissions):#参数是某种权限，检查用户是否有某种权限
        return self.role is not None and \
            (self.role.permissions&permissions)==permissions#位与操作

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def gravatar(self,size=100,default='identicon',rating='g'):
        if request.is_secure:
            url='https://secure.gravatar.com/avatar'
        else:
            url='http://www.gravatar.com/avatar'
        hash=self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
                url=url,hash=hash,size=size,default=default,rating=rating)

    @staticmethod#生成虚拟用户和博客文章
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u=User(
                   email=forgery_py.internet.email_address(),#地址信息
                   username=forgery_py.internet.user_name(True),
                   password=forgery_py.lorem_ipsum.word(),
                   confirmed=True,
                   name=forgery_py.name.full_name(),
                   location=forgery_py.address.city(),
                   about_me=forgery_py.lorem_ipsum.sentence(),
                   member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:#forgery_by随机生成的信息可能在数据库中有重复，抛出integrityError异常
                db.session.rollback()#回滚会话，生成重复内容不会写入数据库

    # def __repr__(self):
    #     return '<User %r>' % self.username

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):#用户未登录时current_user的值
    def can(self,permissions):#未登录可以调用can(),is_administrator()
        return False

    def is_administrator(self):#但是没有任何的权限
        return False

login_manager.anonymous_user=AnonymousUser

@login_manager.user_loader#加载用户的回调函数
def load_user(user_id):
    return User.query.get(int(user_id))#参数Unicode字符串形式表示的用户标识符，返回用户对象


