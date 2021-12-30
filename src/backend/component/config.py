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

import os

"""
ALL Component Config
Include: BK(APP_ID, APP_SECRET)
"""

BK_APP_ID = os.getenv('BK_APP_ID', '')
BK_APP_SECRET = os.getenv('BK_APP_SECRET', '')
BK_GET_TOKEN_URL = os.getenv('BK_GET_TOKEN_URL', '')
BK_REFRESH_TOKEN_URL = os.getenv('BK_REFRESH_TOKEN_URL', '')

BK_PAAS_DOMAIN = os.getenv('BK_PAAS_DOMAIN', '')
BK_CHAT_DOMAIN = os.getenv('BK_CHAT_DOMAIN', '')
BK_JOB_DOMAIN = os.getenv('BK_JOB_DOMAIN', '')
BK_SOPS_DOMAIN = os.getenv('BK_SOPS_DOMAIN', '')
BK_DEVOPS_DOMAIN = os.getenv('BK_DEVOPS_DOMAIN', '')
BK_ITSM_DOMAIN = os.getenv('BK_ITSM_DOMAIN', '')

BK_CC_ROOT = os.getenv('BK_CC_ROOT', '')
BK_JOB_ROOT = os.getenv('BK_JOB_ROOT', '')
BK_SOPS_ROOT = os.getenv('BK_SOPS_ROOT', '')
BK_DEVOPS_ROOT = os.getenv('BK_DEVOPS_ROOT', '')
BK_DATA_ROOT = os.getenv('BK_DATA_ROOT', '')
BK_ITSM_ROOT = os.getenv('BK_ITSM_ROOT', '')
BACKEND_ROOT = os.getenv('BACKEND_ROOT', '')
PLUGIN_ROOT = os.getenv('PLUGIN_ROOT', '')

BK_DATA_TOKEN = os.getenv('BK_DATA_TOKEN', '')
PLUGIN_TOKEN = os.getenv('PLUGIN_TOKEN', '')
BK_SUPER_USERNAME = os.getenv('BK_SUPER_USERNAME', '')

AES_KEY = os.getenv('DATA_AES_KEY', '')
AES_IV = os.getenv('DATA_AES_IV', '')

REDIS_DB_PASSWORD = os.getenv('REDIS_DB_PASSWORD', '')
REDIS_DB_PORT = int(os.getenv('REDIS_DB_PORT', 50117))
REDIS_DB_NAME = os.getenv('REDIS_DB_NAME', '')

ES_DB_DOMAIN = os.getenv('ES_DB_DOMAIN', '')
ES_DB_PORT = int(os.getenv('ES_DB_PORT', 32051))
ES_DB_USERNAME = os.getenv('ES_DB_USERNAME', '')
ES_DB_PASSWORD = os.getenv('ES_DB_PASSWORD', '')
