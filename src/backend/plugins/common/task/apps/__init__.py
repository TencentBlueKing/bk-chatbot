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

from typing import Coroutine, Optional

from opsbot import CommandSession
from component import Cached
from .approval import Approval
from .scheduler import Scheduler
from .authority import Authority


class CallbackHandler(metaclass=Cached):
    def __init__(self, session: CommandSession):
        self.bot_cls = session.bot.type.title().replace('_', '')
        self._session = session
        self._handler = {
            'handle_approval': getattr(Approval(session), self.bot_cls),
            'handle_scheduler': getattr(Scheduler(session), self.bot_cls)
        }

    async def normalize(self, *args) -> Optional:
        action = self._session.ctx.get('action')
        task = getattr(self._handler.get(action), action)(*args)
        if isinstance(task, Coroutine):
            task = await task

        return task
