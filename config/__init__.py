# -*- coding: utf-8 -*-

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
    "APP_CODE",
    "SECRET_KEY",
    "BK_URL",
    "BASE_DIR",
]

import os
import importlib

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from blueapps.core.celery import celery_app


# app 基本信息


def get_env_or_raise(key):
    """Get an environment variable, if it does not exist, raise an exception"""
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            (
                'Environment variable "{}" not found, you must set this variable to run this application.'
            ).format(key),
        )
    return value


# 应用 ID
# APP_CODE = get_env_or_raise('BKPAAS_APP_ID')
# 应用用于调用云 API 的 Secret
# SECRET_KEY = get_env_or_raise('BKPAAS_APP_SECRET')

# 本地开发SaaS运行版本
RUN_VER = 'open'

# 线上SaaS运行版本，如非必要请勿修改
RUN_VER = os.environ.get('BKPAAS_ENGINE_REGION', RUN_VER)

# V3判断环境的环境变量为BKPAAS_ENVIRONMENT
if 'BKPAAS_ENVIRONMENT' in os.environ:
    ENVIRONMENT = os.getenv('BKPAAS_ENVIRONMENT', 'dev')
# V2判断环境的环境变量为BK_ENV
else:
    PAAS_V2_ENVIRONMENT = os.environ.get('BK_ENV', 'development')
    ENVIRONMENT = {'development': 'dev', 'testing': 'stag', 'production': 'prod', }.get(PAAS_V2_ENVIRONMENT)

conf_module = "adapter.sites.{}.config".format(RUN_VER)
_module = importlib.import_module(conf_module)

for _setting in dir(_module):
    if _setting == _setting.upper():
        locals()[_setting] = getattr(_module, _setting)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
