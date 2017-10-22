# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):#登陆表单
	email=StringField(u'邮箱地址',validators=[Required(),Length(1,46),Email()])#length()、Email()验证函数
	password=PasswordField(u'密码',validators=[Required()])
	remember_me=BooleanField(u'记住我')#BoolleanField复选框
	submit=SubmitField(u'登录')

class RegistrationForm(FlaskForm):#注册表单
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64),
                                           Email()])
    username = StringField(u'用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField(u'密码', validators=[
        Required(), EqualTo(u'password2', message='Passwords must match.')])
    password2 = PasswordField(u'证明密码', validators=[Required()])
    submit = SubmitField(u'注册')

    def validate_email(self, field):#验证email在数据库中是否存在
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已使用')

    def validate_username(self, field):#验证username在数据库中是否存在
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已经被占用.')


class ChangePasswordForm(FlaskForm):#改密表单
    old_password = PasswordField(u'Old password', validators=[Required()])
    password = PasswordField(u'New password', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])#EqualTo验证两个密码是否一样，要求附属到上一个密码字段，password2为参数
    password2 = PasswordField('Confirm new password', validators=[Required()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):#改密请求表单
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):#确保两次输入的密码相同
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    password = PasswordField('New Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):#确保填写 的值在数据库中不存在
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(FlaskForm):#改email表单
    email = StringField('New Email', validators=[Required(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

