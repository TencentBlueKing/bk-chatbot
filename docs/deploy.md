# BK_CHATBOT 部署文档


## 依赖第三方组件

* Redis >= 3.2.11
* MongoDB >= 4.2
* 语料库

## 后台服务进程

* bk_chatbot_server

## 部署介绍

### 1. 部署Redis

请参看官方资料 [Redis](https://redis.io/download)

推荐版本下载： [Redis 3.2.11](http://download.redis.io/releases/redis-3.2.11.tar.gz)

注：可采用蓝鲸官方默认Redis
### 2. 部署MongoDB

请参考官方资料 [MongoDB](https://docs.mongodb.com/manual/installation/)

推荐版本下载：[MongoDB 4.2.8](https://www.mongodb.com/dr/fastdl.mongodb.org/linux/mongodb-linux-x86_64-rhel70-4.2.8.tgz/download)

### 3. 配置数据库

1. Redis需要打开auth认证的功能，并为其配置密码

### 4. Release包下载

官方发布的 **Linux Release** 包下载地址见[这里](https://github.com/Tencent/bk-chatbot/releases)


### 5. 机器人后台部署

#### 安装包
> 解压
```
tar -zxf release.tar.gz 或 unzip release.zip
```
* 包的目录结构如下

<img src="resource/img/bk_app_tree.png" alt="image" style="zoom: 80%;" />

> 创建用户配置文件
```
cd release && touch config.py
```
> 添加用户自定义配置，引入机器人默认配置，设置唤醒关键词，定义机器人名称
```
cd release && vim config.py
```

```
import re
from opsbot.default_config import *

RTX_NAME = '我的机器人'
COMMAND_START = ['', re.compile(r'[/!]+')]
```
> 编辑启动文件 server.py, 设置启动Host和Port, 注：该端口要与企业微信应用回调相对应
```
from os import path

import opsbot
import config


if __name__ == '__main__':
    opsbot.init(config)
    opsbot.load_plugins(path.join(path.dirname(__file__), intent', 'plugins'), 'intent.plugins')
    # service on 0.0.0.0:8888
    opsbot.run(host='0.0.0.0', port=8888)
```
> 进入企业微信可查看
* CORPID [查看](http://p.qpic.cn/pic_wework/3036008643/f4f249f8640f1a58ce330176eda833b613ef0c87857592ed/0/)
* SECRET [查看](http://p.qpic.cn/pic_wework/3978463327/cbcd77c7c50cb5da32a41e101af95f6b5a2105e6bf046060/0/)
* TOKEN    用户自定义
* AES_KEY  用户自定义 

> 配置企业微信密钥文件
```
cd release && vim xhttp/decryption/config.py
```

```
"""
Xwork configurations.
"""

CORPID = "必填"   # 企业微信所属企业ID 
FWID = ""
SERVICE_ID = ""
SECRET = "必填"   # 企业微信专属密钥
TOKEN = "必填"    # 企业微信应用自定义Token
AES_KEY = "必填"  # 企业微信应用自定义 aes
```

> 配置蓝鲸API密钥和路径
* 创建蓝鲸SaaS [查看](https://bk.tencent.com/docs/document/6.0/148/6690)
* 获取应用信息[查看](https://bk.tencent.com/docs/document/6.0/148/6391)
* APP 开API访问白名单[查看](https://bk.tencent.com/docs/document/6.0/148/6696)

```
cd release && vim component/config.py
```

```
"""
ALL Component Config
Include: BK(APP_ID, APP_SECRET)
"""

BK_APP_ID = ""             # 你的appid
BK_APP_SECRET = ""         # 你的appkey
BK_GET_TOKEN_URL = ""      # 目前不需要
BK_REFRESH_TOKEN_URL = ""  # 目前不需要

BK_CC_ROOT = ""            # 访问蓝鲸cc的根路径 你的domain + /api/c/compapi/v2/cc/  
BK_JOB_ROOT = ""           # 访问蓝鲸JOB的根路径 你的domain + /api/c/compapi/v2/jobv3/
BK_SOPS_ROOT = ""          # 访问蓝鲸SOPS的根路径 你的domain + /api/c/compapi/v2/sops/
BACKEND_ROOT = ""          # 访问bk-chatbot的根路径 你的domain + /o/bk-chatbot/
```

> 任务执行插件配置

```
cd release && vim intent/plugins/task/settings.py
```

```
"""
REDIS 路径
"""
REDIS_DB_PASSWORD = '' # 访问密码
REDIS_DB_PORT = 6379   # 默认端口
REDIS_DB_NAME = ''     # redis 启动的地址

"""
交互配置
"""

SESSISON_FINISHED_MSG = '本次会话结束，您可以开启新的会话'
SESSISON_FINISHED_CMD = '结束'

TASK_ALLOW_CMD = '是'
TASK_REFUSE_CMD = '否'
TASK_EXEC_SUCCESS = '任务启动成功'
TASK_EXEC_FAIL = '任务启动失败'
```

> 更多机器人个性化配置, 请参照

```
cd release && cat opsbot/default_config.py
```

#### 启动后台服务

```
cd release && ./control start
```

#### 停止后台服务

```
cd release && ./control stop
```

### 6.前端部署
> 开发者中心--应用创建，创建应用

> 创建测试/正式环境数据库

```
CREATE DATABASE IF NOT EXISTS 'stag_db/prod_db' DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
```

> 在APP代码中配置数据库信息
```
/adapter/sites/open/config/stag.py 和 /adapter/sites/open/config/prod.py
新增配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'stag_db/prod_db',
        'USER': 'xxx',
        'PASSWORD': 'xxx',
        'HOST': 'xxxx',
        'PORT': 'xxxx',
    },
}
```

> 环境变量配置(开发者中心--对应APP--应用管理--环境变量)

```
# mongodb信息
BKAPP_MONGO_DB_IP
BKAPP_MONGO_DB_NAME
BKAPP_MONGO_DB_PASSWORD
BKAPP_MONGO_DB_PORT
# redis 信息
BKAPP_REDIS_DB_NAME
BKAPP_REDIS_DB_PASSWORD
BKAPP_REDIS_DB_PORT
# 跨域信息
BKAPP_CORS_ORIGIN_WHITELIST(配置CORS_ORIGIN_WHITELIST)
BKAPP_CSRF_COOKIE_DOMAIN (配置CSRF_COOKIE_DOMAIN)

```
> 选择代码分支/tag，点击部署即可


### 7. 企业微信绑定
> 企业微信后台
* [打开](https://work.weixin.qq.com/wework_admin)

<img src="resource/img/xwork_index.png" alt="image" style="zoom: 67%;" />

> 创建应用
* 进入 应用管理 -> [创建应用](https://work.weixin.qq.com/wework_admin/frame#apps/createApiApp)

![image](resource/img/xwork_app_create.png)

<img src="resource/img/xwork_app_create2.png" alt="image" style="zoom: 67%;" />

> 应用管理
* 点击应用

<img src="resource/img/xwork_app_manage.png" alt="image" style="zoom:67%;" />

<img src="resource/img/xwork_app_manage2.png" alt="image" style="zoom:67%;" />

> 注册回调
* 后台启动服务
* 测试注册 (注：这里url要填写你后台服务部署的外网IP，确保端口开通)

<img src="resource/img/xwork_app_callback.png" alt="image" style="zoom:67%;" />

### 8. 其他
> 社区版HOST配置
```
{你社区版nginx所在服务器} {你自定义的域名} 
```
> bk-chatbot 后台服务启动地址跟企业微信回调地址一致 否则收不到消息