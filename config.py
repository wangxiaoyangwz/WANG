
# -*- coding: utf-8 -*-
import os
basedir=os.path.abspath(os.path.dirname(__file__))

class Config:#基类包含通用配置
    SECRET_KEY=os.environ.get('SECRET_KEY')or 'hard to guess string'#密钥
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True#请求结束自动提交数据库变动
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    #client.UseDefaultCredentials = true;
    MAIL_USERNAME = '1161652587@qq.com'
    MAIL_PASSWORD = 'kbgvjvaqubjggcga'
    FLASKY_MAIL_SUBJECT_PREFIX='[WANG]'#邮件主题前缀
    FLASKY_MAIL_SENDER = '1161652587@qq.com'#发件人地址
    FLASKY_ADMIN = '1161652587@qq.com'#从环境变量中获取收件人地址
    FLASKY_POSTS_PER_PAGE = 20

    @staticmethod#执行对当前环境的配置的初始化，参数是程序实例
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

#子类分别定义专用配置

class TestingConfig(Config):
    TESTING=True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
        
@classmethod
def init_app(cls, app):
    Config.init_app(app)

    # email errors to the administrators
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    secure = None
    if getattr(cls, 'MAIL_USERNAME', None) is not None:
        credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
        if getattr(cls, 'MAIL_USE_TLS', None):
            secure = ()
    mail_handler = SMTPHandler(
        mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
        fromaddr=cls.FLASKY_MAIL_SENDER,
        toaddrs=[cls.FLASKY_ADMIN],
        subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
        credentials=credentials,
        secure=secure)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

class HerokuConfig(ProductionConfig):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)


config={#config字典注册了不同配置环境
    'development':DevelopmentConfig,
    'testing':TestingConfig,
    'production': ProductionConfig,

    'default':DevelopmentConfig#注册默认配置，开发环境
}
