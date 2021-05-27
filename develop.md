## 开发文档

1. 准备本地 rabbitmq 资源
在本地安装 rabbitmq，并启动 rabbitmq-server，服务监听的端口保持默认（5672）。

2. 准备本地 redis 资源  
在本地安装 redis，并启动 redis-server，服务监听的端口保持默认（6379）。

3. 准备本地 mysql
在本地安装 mysql，并启动 mysql-server，服务监听的端口保持默认（3306）。

4. 安装 python 和包
在本地安装 python3.6.7 和 pip，通过 git 拉取源代码到工程目录后，并进入目录下运行 pip 命令安装 python 包。

```bash
pip install -r requirements.txt
```


5. 配置本地环境变量和数据库

1) 设置环境变量  
设置环境变量的目的是让项目运行时能正确获取以下变量的值：    

`BKPAAS_URL`设置为你的社区版蓝鲸地址，比如`http://bk.paas.abc.com`     
`APP_ID`设置为你的社区版应用ID        
`APP_TOKEN`设置为你的社区版应用TOKEN      

具体请参考`adapter/sites/open/dev.env`文件中的设置，可以直接加载到`Pycharm`中使用，或者执行以下命令设置到当前终端：     
```
for va in `cat adapter/sites/open/dev.env|grep -v '#'`; do export $va; done
```

2) 修改 config/dev.py，设置本地开发用的数据库信息，添加 Redis 本地信息

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 默认用mysql
        'NAME': APP_ID,       # 数据库名 (默认与APP_ID相同)
        'USER': 'root',       # 你的数据库user
        'PASSWORD': '',       # 你的数据库password
        'HOST': 'localhost',  # 数据库HOST
        'PORT': '3306',       # 默认3306
    },
}

REDIS = {
    'host': 'localhost',
    'port': 6379,
}
```


6. 创建并初始化数据库  

1) 在 mysql 中创建名为 bk_chatbot 的数据库
```sql
CREATE DATABASE `bk_chatbot` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
```

2) 在工程目录下执行以下命令初始化数据库
```bash
python manage.py migrate
python manage.py createcachetable django_cache
```


7. 打包并收集前端静态资源

1）安装依赖包  
进入 frontend/，执行以下命令安装
```bash
npm install
```

2）本地打包
在 frontend/ 目录下，继续执行以下命令打包前端静态资源
```bash
npm run build
```

8. 配置本地 hosts  
windows: 在 C:\Windows\System32\drivers\etc\host 文件中添加“127.0.0.1 dev.{BKPAAS_URL}”。  
mac: 执行 “sudo vim /etc/hosts”，添加“127.0.0.1 dev.{BKPAAS_URL}”。


9. 启动进程
```bash
python manage.py celery worker -l info
python manage.py celery beat -l info
python manage.py runserver 8000
```


10. 访问页面  
使用浏览器开发 http://dev.{BKPAAS_URL}:8000/ 访问应用。
