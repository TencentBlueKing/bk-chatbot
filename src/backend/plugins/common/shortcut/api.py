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

from typing import Dict, Union

from opsbot import CommandSession
from opsbot.models import BKShortcutTask
from opsbot.plugins import GenericTask
from component import OrmClient, RedisClient
from .settings import (
    SHORTCUT_PROTO, SHORTCUT_COMMON_LABEL, SHORTCUT_WELCOME_TIP,
    SHORTCUT_DELETE_TITLE, SHORTCUT_DELETE_SUBMIT_TEXT
)


class ShortcutHandler(GenericTask):
    """
    deal with alias or shortcut call
    save setting and directly run platform plugin
    """
    def __init__(self, session: CommandSession, name: str = None, bk_biz_id: Union[str, int] = None):
        super().__init__(session, bk_biz_id, RedisClient(env='prod'))
        self.name = name
        self.orm_client = OrmClient()

    def validate_name(self):
        return len(self.name) > 8 \
               and self.orm_client.query(BKShortcutTask, 'count', bk_biz_id=self.biz_id,
                                         bk_username=self.user_id) < 10\
               and self.orm_client.query(BKShortcutTask, 'count', bk_biz_id=self.biz_id,
                                         bk_username=self.user_id, name=self.name) == 0

    def save(self, platform: str, info: Dict):
        shortcut_task = BKShortcutTask(name=self.name, bk_biz_id=int(self.biz_id), bk_platform=platform,
                                       bk_username=self.user_id, params=info)
        self.orm_client.add(shortcut_task)

    def find_one(self):
        return self.orm_client.query(BKShortcutTask, 'first', bk_biz_id=self.biz_id,
                                     bk_username=self.user_id, name=self.name)

    def find_all(self):
        shortcuts = self.orm_client.query(BKShortcutTask, 'all', bk_biz_id=self.biz_id, bk_username=self.user_id)
        return [{'id': str(item.id), 'text': item.name, 'is_checked': False} for item in shortcuts[:20]]

    async def execute_task(self, shortcut: BKShortcutTask):
        flow = SHORTCUT_PROTO[shortcut.bk_platform](self._session)
        result = await flow.execute_task(shortcut.params)
        return getattr(flow, f'render_{shortcut.bk_platform.lower()}_execute_msg')(result, shortcut.params)

    def render_shortcut_list(self):
        shortcuts = self.find_all()
        return self._session.bot.send_template_msg('render_task_list_msg',
                                                   SHORTCUT_COMMON_LABEL,
                                                   SHORTCUT_WELCOME_TIP,
                                                   SHORTCUT_DELETE_TITLE,
                                                   'bk_shortcut_id',
                                                   shortcuts,
                                                   'bk_shortcut_delete',
                                                   submit_text=SHORTCUT_DELETE_SUBMIT_TEXT)

    def delete(self):
        shortcut_id = self._session.bot.parse_action('parse_select', self._session.ctx)
        if not shortcut_id:
            return None

        shortcut = self.orm_client.query(BKShortcutTask, 'first', id=int(shortcut_id))
        self.orm_client.delete(shortcut)
        return shortcut.name
