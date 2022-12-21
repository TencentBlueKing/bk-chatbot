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

from opsbot.adapter import Bot
from opsbot.event import EventHandler
from opsbot.self_typing import Context_T


class SlackEventHandler:
    event = [
        'bk_chat_welcome|bk_cc_biz_select',
        'bk_chat_welcome|bk_chat_app_select',
        'bk_chat_select_task|bk_task_option_select'
    ]

    def __init__(self, bot: Bot, ctx: Context_T):
        self.bot = bot
        self.ctx = ctx
        self.event_handler = EventHandler(*self.event)
        # register
        self.event_handler.link(self._handle_biz_select, 'bk_chat_welcome|bk_cc_biz_select')
        self.event_handler.link(self._handle_app_select, 'bk_chat_welcome|bk_chat_app_select')
        self.event_handler.link(self._handle_option_select, 'bk_chat_select_task|bk_task_option_select')

    async def _handle_biz_select(self):
        select_id = self.ctx['actions'][0]['selected_options'][0]['value']
        attachments = self.ctx['original_message']['attachments']
        for option in attachments[0]['actions'][0]['options']:
            if select_id == option['value']:
                attachments[0]['actions'][0]['selected_options'] = [
                    {
                        'value': select_id,
                        'text': option['text']
                    }
                ]
        await self.bot.call_action('chat_update',
                                   channel=self.ctx['msg_group_id'],
                                   ts=self.ctx['message_ts'],
                                   attachments=attachments)
        return True

    def _handle_app_select(self):
        select_id = self.ctx['actions'][0]['value']
        attachments = self.ctx['original_message']['attachments']
        self.ctx['actions'][0] = {
            'type': 'select',
            'selected_options': attachments[0]['actions'][0]['selected_options']
        }
        self.ctx['message'] = self.bot._message_class(select_id)
        return False

    def _handle_option_select(self):
        select_id = self.ctx['actions'][0]['value']
        return False
