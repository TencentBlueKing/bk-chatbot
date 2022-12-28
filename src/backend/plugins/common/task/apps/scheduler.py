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

from typing import Dict

from opsbot import CommandSession
from component import BKCloud


class Scheduler:
    session = None
    backend = None
    keys = ['intent', 'slots', 'user_id', 'group_id']

    def __new__(cls, session: CommandSession, is_callback=True):
        cls.session = session
        if not is_callback:
            cls.backend = BKCloud().bk_service.backend
        return cls

    @classmethod
    async def list_scheduler(cls):
        def render_func(x):
            return {
                'id': str(x['id']),
                'text': f'{x["biz_id"]} {x["timer_name"]} {x["execute_time"]}',
                'is_checked': False
            }
        data = await cls.backend.get_timer(timer_user=cls.session.ctx['msg_sender_id'])
        msg_template = cls.session.bot.send_template_msg('render_task_list_msg',
                                                         'BKCHAT',
                                                         'BKCHAT定时任务',
                                                         f'当前定时任务如下:',
                                                         'bk_chat_timer_id',
                                                         data,
                                                         'bk_chat_timer_select',
                                                         submit_text='删除',
                                                         render=render_func)
        return msg_template

    @classmethod
    async def delete_scheduler(cls, timer_id: int):
        await cls.backend.delete_timer(timer_id)

    class Xwork:
        @staticmethod
        def handle_scheduler(payload: Dict):
            return {k: payload.get(k) for k in Scheduler.keys if k in payload}
