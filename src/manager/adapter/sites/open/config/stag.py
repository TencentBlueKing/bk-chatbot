# -*- coding: utf-8 -*-
from .default import *  # noqa

BKDATA_URL = f"{os.getenv('BK_PAAS_HOST', '')}/t/bk_dataweb"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("BKAPP_GCS_MYSQL_NAME"),  # 数据库名
        "USER": os.environ.get("BKAPP_GCS_MYSQL_USER"),  # 数据库用户
        "PASSWORD": os.environ.get("BKAPP_GCS_MYSQL_PASSWORD"),  # 数据库密码
        "HOST": os.environ.get("BKAPP_GCS_MYSQL_HOST"),  # 数据库主机
        "PORT": os.environ.get("BKAPP_GCS_MYSQL_PORT", "3306"),  # 数据库端口
    }
}
