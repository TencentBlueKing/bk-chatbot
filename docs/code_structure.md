# 代码结构

```
├── adapter
├── bin
├── common
├── config
├── docs
├── LICENSE
├── LICENSE.txt
├── manage.py
├── Procfile
├── pyproject.toml
├── pytest.ini
├── README_en.md
├── README.md
├── requirements.txt
├── runtime.txt
├── scripts
├── settings.py
├── settings_test.py
├── setup.cfg
├── src
├── urls.py
├── VERSION
└── wsgi.py
```

代码模块分为『bkchat机器人(backend)』、『bkchat管理端(manager)』、『前端展示web』三个部分，混合了vue/python/shell等几种语言

##源码介绍(src)
* 总揽
```
.
├── backend         #im后台
├── __init__.py
└── manager         #web管理端后台
```

* manager
```
.
├── conftest.py
├── handler
├── __init__.py
├── LICENSE.txt
├── locale
├── module_api       #各类api包含job，sops，devops等
├── module_biz       #业务配置与蓝鲸cmdb平台打通
├── module_index
├── module_inside    
├── module_intent    #意图配置
├── module_nlp       #语料管理模块
├── module_other     
├── module_plugin    #公共插件管理模块
├── module_timer     #定时器模块与job打通
├── runtime.txt
├── settings.py
├── static
├── templates
└── urls.py
```

* backend
```
.
├── component      #组件api模块
├── control        #控制脚本
├── Dockerfile     #docker编辑文件
├── opsbot         #后台主逻辑
├── plugins        #插件模块
├── protocol       #im协议模块
├── requirements.txt
└── server.py      
```
