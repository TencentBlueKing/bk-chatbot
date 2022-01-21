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
import time
from typing import Union, Optional, Dict, List

from opsbot import CommandSession


class GenericTask:
    def __init__(self, session: CommandSession, bk_biz_id: Union[str, int] = None, redis_client: Optional = None):
        self._session = session
        self.user_id = self._session.ctx['msg_sender_id']
        self.biz_id = bk_biz_id
        self.set_biz(redis_client)

    def set_biz(self, redis_client: Optional):
        if redis_client:
            if self.biz_id:
                redis_client.hash_set('chat_single_biz', self.user_id, self.biz_id)
            else:
                if self._session.ctx['msg_from_type'] == 'single':
                    self.biz_id = redis_client.hash_get("chat_single_biz", self.user_id)
                else:
                    self.biz_id = redis_client.hash_get("chat_group_biz", self._session.ctx['msg_group_id'])

    @abc.abstractmethod
    def execute_task(self) -> bool:
        raise NotImplementedError

    @classmethod
    def render_execute_msg(cls, platform: str, task_result: bool, task_name: str,
                           parameter: List, task_domain: str) -> Dict:
        return {
            'card_type': 'text_notice',
            'source': {
                'desc': platform
            },
            'main_title': {
                'title': f'{task_name}启动成功' if task_result else f'{task_name}启动失败'
            },
            'horizontal_content_list': parameter,
            'task_id': str(int(time.time() * 100000)),
            'card_action': {
                'type': 1,
                'url': task_domain
            }
        }
