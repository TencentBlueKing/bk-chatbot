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

from common.utils.os import get_env_or_raise

STAG_PLUGIN_URI_ENV = "STAG_PLUGIN_URI"  # 测试环境插件URL的环境变量
PROD_PLUGIN_URI_ENV = "PROD_PLUGIN_URI"  # 正式环境插件URL的环境变量
PLUGIN_ITSM_SERVICE_ID = get_env_or_raise("PLUGIN_ITSM_SERVICE_ID")  # 插件审批服务ID
PLUGIN_ITSM_CALLBACK_URI = get_env_or_raise("PLUGIN_ITSM_CALLBACK_URI")  # 插件审核回调地址
PLUGIN_RELOAD_URI = get_env_or_raise("PLUGIN_RELOAD_URI")  # 机器人reload地址
PROD_BOT_NAME = get_env_or_raise("PROD_BOT_NAME")  # 正式环境机器人名称
STAG_BOT_NAME = get_env_or_raise("STAG_BOT_NAME")  # 测试环境机器人名称
