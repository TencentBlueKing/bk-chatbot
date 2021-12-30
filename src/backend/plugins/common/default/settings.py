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
DEFAULT_WELCOME_INTENT = [
    {
        'key': 'release',
        'name': '版本验证与发布',
        'detail': [
            {'text': 'rel2提免测单', 'key': 'INTERNAL_PLUGIN_RPC_REL2'},
            {'text': '查询rel单据', 'key': 'INTERNAL_PLUGIN_RPC_REL2_List'},
            {'text': '安卓加固', 'key': 'INTERNAL_PLUGIN_RPC_ANDROID'},
            {'text': 'ios签名', 'key': 'INTERNAL_PLUGIN_RPC_IOS'},
            {'text': '查询itest单据', 'key': 'INTERNAL_PLUGIN_RPC_ITEST_List'},
            {'text': 'itest提单', 'key': 'INTERNAL_PLUGIN_RPC_ITEST'},
            {'text': 'itest转rel', 'key': 'INTERNAL_PLUGIN_RPC_REL2_ITEST'},
            {'text': '飞鹰公告', 'key': 'INTERNAL_PLUGIN_RPC_EAGLEV5'},
            {'text': '创建云石FTP下载链接', 'key': 'INTERNAL_PLUGIN_RPC_CLOUD-STONE'},
            {'text': 'AMS公告', 'key': 'INTERNAL_PLUGIN_RPC_AMS'}
        ],
        'is_open': True
    },
    {
        'key': 'check',
        'name': '游戏业务数据查询',
        'detail': [
            {'text': 'QQ、微信号转openid', 'key': 'INTERNAL_PLUGIN_RPC_OPENID'},
            {'text': '业务信息查询', 'key': 'INTERNAL_PLUGIN_RPC_BUSINESS'},
            {'text': 'L5配置查询', 'key': 'INTERNAL_PLUGIN_RPC_POLARIS_List'}
        ],
        'is_open': True
    },
    {
        'key': 'operation',
        'name': '运维工具',
        'detail': [
            {'text': '云石FTP白名单添加', 'key': 'INTERNAL_PLUGIN_RPC_CLOUD_STONE'},
            {'text': 'WMAN打补丁', 'key': 'INTERNAL_PLUGIN_RPC_WMAN'},
            {'text': '查询负载均衡', 'key': 'INTERNAL_PLUGIN_RPC_CLB'},
            {'text': '域名查询', 'key': 'INTERNAL_PLUGIN_RPC_GSLB'}
        ],
        'is_open': True
    }
]
DEFAULT_TOOL_EXTRA = [
    {
        'content': f'通用{os.getenv("DEFAULT_EXTRA_TOOL", "运营")}工具请点击',
        'type': 'click',
        'key': lambda biz_name, biz_id, user_id: f'opsbot_tool_extra|{biz_id}|{user_id}',
        'text': f'{os.getenv("DEFAULT_EXTRA_TOOL", "运营")}工具\n'
    }
]
DEFAULT_TOOL_BAR = [
    {
        'content': DEFAULT_WELCOME_TASK,
        'type': 'click',
        'key': lambda biz_name, biz_id, user_id: f'opsbot_intent|{biz_id}|{user_id}',
        'text': '技能\n'
    },
    {
        'content': DEFAULT_DEVOPS_MSG,
        'type': 'click',
        'key': lambda biz_name, biz_id, user_id: f'devops_project|{biz_id}|{user_id}',
        'text': '流水线\n'
    },
    {
        'content': DEFAULT_HELP_MSG,
        'type': 'click',
        'key': lambda biz_name, biz_id, user_id: f'opsbot_help|{biz_name}|{user_id}',
        'text': '人工'
    }
]

DEFAULT_BIND_BIZ_ALIAS = ('绑定业务', '切换业务', '解绑业务', '业务绑定', '业务解绑', '业务切换')
DEFAULT_BIND_BIZ_TIP = '查到你名下没有业务'
DEFAULT_HELPER = os.getenv('DEFAULT_HELPER', '').split(',')
DEFAULT_INTENT_CATEGORY = os.getenv('DEFAULT_INTENT_CATEGORY', '').split(',')
