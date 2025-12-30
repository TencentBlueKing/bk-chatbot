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

from typing import Coroutine
from functools import wraps

from opsbot import CommandSession
from opsbot.models import BKExecutionLog
from component import OrmClient


def on_admin(func):
    @wraps(func)
    async def wrapper(session: CommandSession, *args, **kwargs):
        if session.ctx['msg_sender_id'] in session.bot.config.SUPERUSERS:
            result = func(session, *args, **kwargs)
            if isinstance(result, Coroutine):
                result = await result
            return result
    return wrapper


class Stat:
    def __init__(self):
        self.orm_client = OrmClient()

    def stat_execution(self):
        return self.orm_client.query(BKExecutionLog, 'count')
