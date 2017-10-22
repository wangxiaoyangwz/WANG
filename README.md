### WANG--打开方法
======

1、这个项目是一个社交博客网站
2、有的功能
       1）登录、注册、认证、个人资料、写博客等
打开的方法：
`python manage.py renserver --host 0.0.0.0`

如果发生数据库问题，解决方法：
1.删除migrates文件夹
2.执行`python manage.py db init`
-->   `python manage.py migrate`
-->  `python manage.py upgrade`
`python manage.py renserver --host 0.0.0.0`
先要创建一个虚拟环境
`virtrualenv <虚拟环境的名字>`
并打开虚拟环境
`<虚拟环境的名字>`\scripts\activate`

对于其中需要的扩展或者插件使用
`pip install -r requirements.txt`
将所有需要的扩展下载好
`python manage.py renserver --host 0.0.0.0`


