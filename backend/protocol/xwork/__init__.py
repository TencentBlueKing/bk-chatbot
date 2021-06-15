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

from . import config as XworkConfig
from .proxy import Proxy as XworkProxy
from ..in_xwork import log_message
from ..in_xwork.message import Message, MessageSegment
from opsbot.adapter import Bot as BaseBot
from opsbot.self_typing import Context_T
from opsbot.log import logger
from opsbot.command import handle_command, SwitchException
from opsbot.natural_language import handle_natural_language
from opsbot.permission import IS_SUPERUSER, IS_PRIVATE, IS_GROUP_MEMBER

_message_preprocessors = set()

_min_context_fields = (
    'msg_sender_id',
)

_MinContext = namedtuple('MinContext', _min_context_fields)


class Bot(BaseBot, XworkProxy):
    protocol_config: Dict = None

    def __init__(self, config_object: Optional[Any] = None):
        if config_object is None:
            from opsbot import default_config as config_object

        self.config = config_object
        self.protocol_config = {k: v for k, v in XworkConfig.__dict__.items()}
        XworkProxy.__init__(self, self.config.API_ROOT, self.protocol_config)
        self.asgi.debug = self.config.DEBUG

        @self.on_text
        async def _(ctx):
            asyncio.ensure_future(self.handle_message(ctx))

        @self.on_event
        async def _(ctx):
            asyncio.ensure_future(self.handle_event(ctx))

    @property
    def type(self) -> str:
        return "xwork"

    @cached(ttl=2 * 60)
    async def _check(self, min_ctx: _MinContext, permission_required: int) -> bool:
        permission = 0
        if min_ctx.msg_sender_id in self.config.SUPERUSERS:
            permission |= IS_SUPERUSER
        else:
            permission |= IS_PRIVATE

        return bool(permission & permission_required)

    async def check_permission(self, ctx: Context_T, permission_required: int) -> bool:
        min_ctx_kwargs = {}
        for field in _min_context_fields:
            if field in ctx:
                min_ctx_kwargs[field] = ctx[field]
            else:
                min_ctx_kwargs[field] = None
        min_ctx = _MinContext(**min_ctx_kwargs)
        return await self._check(min_ctx, permission_required)

    async def handle_message(self, ctx: Context_T):
        log_message(ctx)

        ctx['to_me'] = True
        if not ctx['message']:
            ctx['message'].append(MessageSegment.text(''))

        cor_os = []
        for processor in _message_preprocessors:
            cor_os.append(processor(self, ctx))
        if cor_os:
            await asyncio.wait(cor_os)

        while True:
            try:
                handled = await handle_command(self, ctx)
                break
            except SwitchException as e:
                # we are sure that there is no session existing now
                ctx['message'] = e.new_ctx_message
                ctx['to_me'] = True
        if handled:
            logger.info(f'Message {ctx["msg_id"]} is handled as a command')
            return

        handled = await handle_natural_language(self, ctx)
        if handled:
            logger.info(f'Message {ctx["msg_id"]} is handled '
                        f'as natural language')
            return

    async def handle_event(self, ctx: Context_T):
        pass

    async def call_api(self, action: str, **params):
        pass