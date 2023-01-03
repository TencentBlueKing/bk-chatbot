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

BK_ENV = os.getenv('BK_ENV', 'oa,iegcom,obk,intlgame').split(',')
BK_SUPER_USERNAME = os.getenv('BK_SUPER_USERNAME', '')

PLUGIN_ROOT = os.getenv('PLUGIN_ROOT', '')
PLUGIN_TOKEN = os.getenv('PLUGIN_TOKEN', '')

JIRA_ROOT = os.getenv("JIRA_ROOT", "")
JIRA_USER_EMAIL = os.getenv('JIRA_USER_EMAIL', '')
JIRA_TOKEN = os.getenv('JIRA_TOKEN', '')
JIRA_DOMAIN = os.getenv('JIRA_DOMAIN', '')

AES_KEY = os.getenv('DATA_AES_KEY', '')
AES_IV = os.getenv('DATA_AES_IV', '')

REDIS_DB_PASSWORD = os.getenv('REDIS_DB_PASSWORD', '')
REDIS_DB_PORT = int(os.getenv('REDIS_DB_PORT', 50117))
REDIS_DB_NAME = os.getenv('REDIS_DB_NAME', '')

ES_DB_DOMAIN = os.getenv('ES_DB_DOMAIN', '')
ES_DB_PORT = int(os.getenv('ES_DB_PORT', 32051))
ES_DB_USERNAME = os.getenv('ES_DB_USERNAME', '')
ES_DB_PASSWORD = os.getenv('ES_DB_PASSWORD', '')

ORM_URL = os.getenv('ORM_URL', '')
