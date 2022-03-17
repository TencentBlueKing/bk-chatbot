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

import time

from opsbot import CommandSession
from opsbot.models import BKExecutionLog
from component import RedisClient, CC, Backend, Plugin, OrmClient


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
        return self._session.bot.send_template_msg('render_welcome_msg', data, bk_biz_id)

    async def render_biz_msg(self):
        data = await self._search_business()
        if not data:
            return None

        return self._session.bot.send_template_msg('render_biz_list_msg', data)

    def bind_cc_biz(self):
        try:
            bk_biz_id = self._session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
        except KeyError:
            return None

        RedisClient(env="prod").hash_set('chat_single_biz', self.user_id, bk_biz_id)
        return bk_biz_id


class Stat:
    def __init__(self):
        self.orm_client = OrmClient()

    def stat_execution(self):
        return self.orm_client.query(BKExecutionLog, 'count')
