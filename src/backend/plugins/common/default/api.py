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

from opsbot import CommandSession
from opsbot.models import BKExecutionLog
from opsbot.plugins import GenericTool
from component import RedisClient, OrmClient, BKCloud
from .settings import DEFAULT_BIND_BIZ_TIP


class Flow:
    def __init__(self, session: CommandSession):
        self._session = session
        self.user_id = self._session.ctx['msg_sender_id']
        self.cc = BKCloud(env='v7').bk_service.cc

    async def _search_business(self):
        response = await self.cc.search_business(bk_username=self.user_id, fields=["bk_biz_id", "bk_biz_name"])
        return response.get('info', [])

    async def render_welcome_msg(self):
        bk_data = GenericTool.get_biz_data(self._session, RedisClient(env="prod"))
        bk_biz_id = bk_data.get('biz_id')
        data = await self._search_business()
        if not data:
            return self._session.bot.send_template_msg('render_markdown_msg', '<bold>CC:<bold>',
                                                       DEFAULT_BIND_BIZ_TIP)
        return self._session.bot.send_template_msg('render_welcome_msg', data, bk_biz_id)

    async def render_biz_msg(self):
        data = await self._search_business()
        if not data:
            return None

        return self._session.bot.send_template_msg('render_biz_list_msg', data)

    def bind_cc_biz(self):
        bk_biz_id = self._session.bot.parse_action('parse_select', self._session.ctx)
        if not bk_biz_id:
            return None
        GenericTool.set_biz_data(self._session, RedisClient(env="prod"), bk_biz_id)
        return bk_biz_id
