"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云PaaS平台社区版 (BlueKing PaaSCommunity Edition) available.
Copyright (C) 2017-2018 THL A29 Limited,
a Tencent company. All rights reserved.
Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

__all__ = [
    "celery_app",
    "RUN_VER",
    "BASE_DIR",
]

import importlib
import os

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from blueapps.core.celery import celery_app

# app 基本信息


def get_env_or_raise(key):
    """Get an environment variable, if it does not exist, raise an exception"""
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            ('Environment variable "{}" ' "not found, you must set this variable to run this application.").format(key),
        )
    return value


# 应用 ID
# APP_CODE = get_env_or_raise('BKPAAS_APP_ID')
# 应用用于调用云 API 的 Secret
# SECRET_KEY = get_env_or_raise('BKPAAS_APP_SECRET')

# 本地开发SaaS运行版本
RUN_VER = "open"

# 线上SaaS运行版本，如非必要请勿修改
RUN_VER = os.environ.get("BKPAAS_ENGINE_REGION", RUN_VER)
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# V3判断环境的环境变量为BKPAAS_ENVIRONMENT
if "BKPAAS_ENVIRONMENT" in os.environ:
    ENVIRONMENT = os.getenv("BKPAAS_ENVIRONMENT", "dev")
# V2判断环境的环境变量为BK_ENV
else:
    PAAS_V2_ENVIRONMENT = os.environ.get("BK_ENV", "development")
    ENVIRONMENT = {
        "development": "dev",
        "testing": "stag",
        "production": "prod",
    }.get(PAAS_V2_ENVIRONMENT)


# redis配置
REDIS_HOST = os.getenv("BKAPP_REDIS_DB_NAME", "localhost")
REDIS_PASSWORD = os.getenv("BKAPP_REDIS_DB_PASSWORD", "")
REDIS_PORT = os.getenv("BKAPP_REDIS_DB_PORT", "6379")

# 适配器部分
conf_module = f"adapter.sites.{RUN_VER}.config"
_module = importlib.import_module(conf_module)
for _setting in dir(_module):
    if _setting == _setting.upper():
        locals()[_setting] = getattr(_module, _setting)

# 加载不同运行环境不同配置
try:
    RUN_VER_CONF = f"config.{RUN_VER}"
    run_ver_conf_module = importlib.import_module(RUN_VER_CONF)
    for _setting in dir(run_ver_conf_module):
        if _setting == _setting.upper():
            locals()[_setting] = getattr(run_ver_conf_module, _setting)
except ImportError:
    pass

# 加载各个版本特殊配置
try:
    conf_module = f"adapter.sites.{RUN_VER}.config.{ENVIRONMENT}"
    _module = importlib.import_module(conf_module)
    for _setting in dir(_module):
        if _setting == _setting.upper():
            locals()[_setting] = getattr(_module, _setting)
except ImportError:
    pass
