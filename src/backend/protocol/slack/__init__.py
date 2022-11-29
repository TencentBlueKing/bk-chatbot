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

from collections import namedtuple
from typing import Any, Optional, Dict

import asyncio
from aiocache import cached

from .proxy import Proxy as SlackProxy
from .message import Message, MessageSegment, MessageTemplate
from opsbot.adapter import Bot as BaseBot
from opsbot.self_typing import Context_T
from opsbot.log import logger
from opsbot.command import handle_command, SwitchException
from opsbot.natural_language import handle_natural_language
from opsbot.permission import (
    IS_SUPERUSER, IS_PRIVATE, IS_GROUP_MEMBER, OPEN_API
)

_message_preprocessors = set()

_min_context_fields = (
    'msg_sender_id',
)

_MinContext = namedtuple('MinContext', _min_context_fields)


class Bot(BaseBot, SlackProxy):
    protocol_config: Dict = None

    def __init__(self, config_object: Optional[Any] = None):
        if config_object is None:
            from opsbot import default_config as config_object

        self.config = config_object
        self.protocol_config = {k: v for k, v in SlackProxy.__dict__.items()}
        SlackProxy.__init__(self, self.config.API_ROOT, self.protocol_config)
        self.asgi.debug = self.config.DEBUG

        @self.on_text
        async def _(ctx):
            asyncio.ensure_future(self.handle_message(ctx))

    @property
    def type(self) -> str:
        return "slack"

    @cached(ttl=2 * 60)
    async def _check(self, min_ctx: _MinContext, permission_required: int) -> bool:
        pass

    async def check_permission(self, ctx: Context_T, permission_required: int) -> bool:
        pass

    async def handle_message(self, ctx: Context_T):
        pass

    async def handle_event(self, ctx: Context_T):
        pass

    async def call_api(self, action: str, **params):
        pass

    def send_template_msg(self, action, *args, **kwargs) -> Dict:
        return getattr(MessageTemplate, action)(*args, **kwargs)
