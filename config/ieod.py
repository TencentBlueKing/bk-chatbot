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

from config import get_env_or_raise

CORS_ORIGIN_WHITELIST = get_env_or_raise("BKAPP_CORS_ORIGIN_WHITELIST").split(",")
CSRF_COOKIE_DOMAIN = get_env_or_raise("BKAPP_CSRF_COOKIE_DOMAIN")
RIO_TOKEN = get_env_or_raise("RIO_TOKEN")

# ieod 特有redis
REDIS_HOST = get_env_or_raise("REDIS_HOST")
REDIS_PASSWORD = get_env_or_raise("REDIS_PASSWORD")
REDIS_PORT = get_env_or_raise("REDIS_PORT")
