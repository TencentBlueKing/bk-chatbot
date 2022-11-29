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

import abc
import json
from typing import Union, Optional, Dict, List

from opsbot import CommandSession
from .settings import PLUGIN_NULL_MSG


class GenericTask:
    def __init__(self, session: CommandSession, bk_biz_id: Union[str, int] = None, redis_client: Optional = None):
        self._session = session
        self.user_id = self._session.ctx['msg_sender_id']
        self.biz_id = bk_biz_id
        self.set_biz(redis_client)

    def set_biz(self, redis_client: Optional):
        # todo adjust bk_env
        if redis_client:
            if not self.biz_id:
                bk_data = GenericTool.get_biz_data(self._session, redis_client)
                self.biz_id = bk_data.get('biz_id')
            else:
                GenericTool.set_biz_data(self._session, redis_client, self.biz_id)

    @abc.abstractmethod
    def execute_task(self) -> bool:
        raise NotImplementedError

    def render_execute_msg(self, platform: str, task_result: bool, task_name: str,
                           parameter: List, task_domain: str) -> Dict:
        return self._session.bot.send_template_msg('render_task_execute_msg', platform, task_name,
                                                   task_result, parameter, task_domain)

    def render_null_msg(self, platform: str) -> Dict:
        return self._session.bot.send_template_msg('render_markdown_msg',
                                                   PLUGIN_NULL_MSG.format(platform))


class GenericTool:
    @staticmethod
    def get_biz_data(session: CommandSession, redis_client) -> Dict:
        if session.ctx['msg_from_type'] == 'single':
            bk_data = redis_client.hash_get(f'{session.bot.config.ID}:chat_single_biz',
                                            session.ctx['msg_sender_id'])
        else:
            bk_data = redis_client.hash_get(f'{session.bot.config.ID}:chat_group_biz',
                                            session.ctx['msg_group_id'])
        try:
            bk_data = json.loads(bk_data)
        except (json.JSONDecodeError, TypeError):
            bk_data = {}
        return bk_data

    @staticmethod
    def set_biz_data(session: CommandSession,
                     redis_client,
                     biz_id: int,
                     biz_name: str = '',
                     bk_env: str = 'v7') -> Dict:
        data = {'biz_id': biz_id, 'biz_name': biz_name,
                'user_id': session.ctx['msg_sender_id'], 'env': bk_env}
        if session.ctx['msg_from_type'] == 'single':
            redis_client.hash_set(f'{session.ctx["msg_group_id"]}:chat_single_biz',
                                  session.ctx['msg_sender_id'], json.dumps(data))
        else:
            redis_client.hash_set(f'{session.ctx["msg_group_id"]}:chat_group_biz',
                                  session.ctx['msg_group_id'], json.dumps(data))
        return data
