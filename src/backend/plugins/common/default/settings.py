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

DEFAULT_SHOW_GROUP_ID_ALIAS = ('群ID', '群id', '查看企业微信ID', '查看企业微信id')

DEFAULT_WELCOME_MSG = '{user} 您好，欢迎使用{name}，很高兴为您服务\n'
DEFAULT_WELCOME_BIZ = '当前已设置常用业务为'
DEFAULT_WELCOME_BIND = '当前未设置常用业务， 如需请点击'
DEFAULT_WELCOME_REBIND = '重新设置请点击'
DEFAULT_WELCOME_TIP = '目前已支持的通用技能 指引请点击'
DEFAULT_WELCOME_TASK = '业务自定义运维工具请点击'
DEFAULT_WELCOME_CONFIG = '配置业务技能请点击'
DEFAULT_HELP_MSG = '如需人工帮助请咨询'
DEFAULT_DEVOPS_MSG = '蓝盾流水线执行请点击'
DEFAULT_GUIDE_MSG = '详细操作指引请点击'
DEFAULT_GUIDE_URL = os.getenv('DEFAULT_GUIDE_URL', '')
DEFAULT_BIZ_TIP = '请选择业务:'
DEFAULT_BIZ_BIND_SUCCESS = '常用业务设置成功，业务ID'
DEFAULT_BIZ_BIND_FAIL = '常用业务设置失败，该群已经绑定其他业务，请前往网页操作'

DEFAULT_BIND_BIZ_ALIAS = ('绑定业务', '切换业务', '解绑业务', '业务绑定', '业务解绑', '业务切换')
DEFAULT_BIND_BIZ_TIP = '查到你名下没有业务'
DEFAULT_HELPER = os.getenv('DEFAULT_HELPER', '').split(',')
DEFAULT_INTENT_CATEGORY = os.getenv('DEFAULT_INTENT_CATEGORY', '').split(',')
