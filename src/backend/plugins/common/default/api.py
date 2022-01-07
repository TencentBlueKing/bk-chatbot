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

import time, json
from typing import List, Callable

from opsbot import CommandSession
from component import RedisClient, CC, Backend, Plugin
from .settings import (
    DEFAULT_WELCOME_MSG, DEFAULT_WELCOME_BIZ, DEFAULT_WELCOME_REBIND,
    DEFAULT_WELCOME_BIND, DEFAULT_WELCOME_INTENT, DEFAULT_INTENT_CATEGORY, DEFAULT_BIZ_TIP,
    DEFAULT_WELCOME_TIP, DEFAULT_TOOL_BAR, DEFAULT_TOOL_EXTRA, DEFAULT_GUIDE_URL
)


class Flow:
    def __init__(self, session: CommandSession):
        self._session = session
        self.user_id = self._session.ctx['msg_sender_id']

    async def _search_business(self):
        response = await CC().search_business(bk_username=self.user_id, fields=["bk_biz_id", "bk_biz_name"])
        data = [{'id': str(biz['bk_biz_id']), 'text': biz['bk_biz_name'], 'is_checked': False}
                for biz in response.get('info')[:20]]
        return data

    async def render_welcome_msg(self):
        bk_biz_id = RedisClient(env="prod").hash_get('chat_single_biz', self.user_id)
        data = await self._search_business()
        template_card = {
            'card_type': 'button_interaction',
            'source': {
                'desc': 'BKCHAT'
            },
            'main_title': {
                'title': '欢迎使用蓝鲸信息流'
            },
            'task_id': str(int(time.time() * 100000)),
            'button_selection': {
                'question_key': 'bk_biz_id',
                'title': '业务',
                'option_list': data[:10],
                'selected_id': bk_biz_id if bk_biz_id else ''
            },
            'action_menu': {
                'desc': '更多操作',
                'action_list': [
                    {'text': '查找任务', 'key': 'bk_app_task_filter'},
                    {'text': '绑定业务', 'key': 'bk_cc_biz_bind'}
                ]
            },
            'horizontal_content_list': [
                {
                    "type": 3,
                    "keyname": "员工信息",
                    "value": "点击查看",
                    "userid": self.user_id
                }
            ],
            'button_list': [
                {
                    "text": "CI",
                    "style": 1,
                    "key": "bk_devops"
                },
                {
                    "text": "JOB",
                    "style": 1,
                    "key": "bk_job"
                },
                {
                    "text": "SOPS",
                    "style": 1,
                    "key": "bk_sops"
                },
                {
                    "text": "ITSM",
                    "style": 1,
                    "key": "bk_itsm"
                }
            ]
        }
        return template_card

    async def render_biz_msg(self):
        data = await self._search_business()
        if not data:
            return None

        template_card = {
            'card_type': 'vote_interaction',
            'source': {
                'desc': 'CC'
            },
            'main_title': {
                'title': '欢迎使用配置平台',
                'desc': '请选择业务'
            },
            'task_id': str(int(time.time() * 100000)),
            'checkbox': {
                'question_key': 'bk_biz_id',
                'option_list': data
            },
            'submit_button': {
                'text': '提交',
                'key': 'bk_cc_biz_select'
            }
        }
        return template_card

    def bind_cc_biz(self):
        try:
            bk_biz_id = self._session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
        except KeyError:
            return None

        RedisClient(env="prod").hash_set('chat_single_biz', self.user_id, bk_biz_id)
        return bk_biz_id
