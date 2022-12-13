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

import re
from collections import namedtuple
from typing import Any, Optional, Dict, Iterable, Union

import asyncio
from aiocache import cached

from opsbot.adapter import Bot as BaseBot
from opsbot.self_typing import Context_T
from opsbot.log import logger
from opsbot.command import handle_command, SwitchException
from opsbot.natural_language import handle_natural_language
from opsbot.permission import (
    IS_SUPERUSER, IS_PRIVATE, IS_GROUP_MEMBER, OPEN_API
)
from .proxy import Proxy as SlackProxy
from .message import (
    Message, MessageSegment, MessageTemplate, MessageParser
)
from . import config as SlackConfig

_message_preprocessors = set()

_min_context_fields = (
    'msg_sender_id',
    'msg_group_id',
)

_MinContext = namedtuple('MinContext', _min_context_fields)


class Bot(BaseBot, SlackProxy):
    protocol_config: Dict = None

    def __init__(self, config_object: Optional[Any] = None):
        if config_object is None:
            from opsbot import default_config as config_object

        self.config = config_object
        self.protocol_config = {k: v for k, v in SlackConfig.__dict__.items()}
        SlackProxy.__init__(self, self.config.API_ROOT, self.protocol_config)
        self.asgi.debug = self.config.DEBUG

        @self.on_event_callback
        async def _(ctx):
            asyncio.ensure_future(self.handle_message(ctx))

        @self.on_interactive_message
        async def _(ctx):
            asyncio.ensure_future(self.handle_event(ctx))

    @property
    def type(self) -> str:
        return "slack"

    @cached(ttl=2 * 60)
    async def _check(self, min_ctx: _MinContext, permission_required: int) -> bool:
        permission = 0
        if min_ctx.msg_sender_id in self.config.SUPERUSERS:
            permission |= IS_SUPERUSER
        else:
            permission |= IS_PRIVATE

        return bool(permission & permission_required)

    async def check_permission(self, ctx: Context_T, permission_required: int) -> bool:
        if self.config.IS_USE_SESSION_WHITELIST:
            if ctx['msg_sender_code'] not in self.protocol_config['USER_WHITE_MAP']:
                return False
            else:
                ctx['msg_sender_id'] = \
                    self.protocol_config['USER_WHITE_MAP'][ctx['msg_sender_code']]

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

        if not ctx['message']:
            ctx['message'].append(MessageSegment.text(''))

        cor_os = []
        for processor in _message_preprocessors:
            cor_os.append(processor(self, ctx))
        if cor_os:
            await asyncio.wait(cor_os)

        raw_to_me = ctx.get('to_me', False)
        _check_at_me(self, ctx)
        _check_calling_me_nickname(self, ctx)
        ctx['to_me'] = raw_to_me or ctx['to_me']

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
        if ctx['msg_type'] == 'interactive_message':
            if ctx['callback_id'] == 'bk_chat_welcome|bk_cc_biz_select':
                select_id = ctx['actions'][0]['select_options'][0]['value']
                attachments = ctx['original_message']['attachments']
                for option in attachments[0]['actions'][0]['options']:
                    if select_id == option['value']:
                        attachments[0]['actions'][0]['selected_options'] = [
                            {
                                'value': select_id,
                                'text': option['text']
                            }
                        ]
                await self.call_action('chat_update',
                                       channel=ctx['msg_group_id'],
                                       ts=ctx['message_ts'],
                                       attachments=attachments)
            return
        ctx['to_me'] = True
        await self.handle_message(ctx)

    async def call_api(self, action: str, **params):
        return await self.call_action(action, **params)

    def send_template_msg(self, action, *args, **kwargs) -> Dict:
        return getattr(MessageTemplate, action)(*args, **kwargs)

    def parse_action(self, action, ctx: Context_T, *args, **kwargs) -> Union[str, Dict]:
        return getattr(MessageParser, action)(ctx, *args, **kwargs)


def _check_at_me(bot: BaseBot, ctx: Context_T) -> None:
    if ctx['msg_from_type'] == 'single':
        ctx['to_me'] = True
    else:
        # group or discuss
        ctx['to_me'] = False
        at_me_seg = bot.config.RTX_NAME
        p = re.compile(rf'[<]{1}[@]{1}{bot.config.RTX_NAME}[>]{1}')
        # check the first segment
        first_msg_seg = ctx['message'][0]
        with p.search(first_msg_seg.data['text']) as result:
            if result:
                ctx['to_me'] = True
                text = first_msg_seg.data['text'].replace(result, "").strip(" ") or 'welcome'
                first_msg_seg.data['text'] = text

        if not ctx['message']:
            ctx['message'].append(MessageSegment.text(''))


def _check_calling_me_nickname(bot: BaseBot, ctx: Context_T) -> None:
    first_msg_seg = ctx['message'][0]
    if first_msg_seg.type != 'text':
        return

    first_text = first_msg_seg.data['text']
    if bot.config.NICKNAME:
        # check if the user is calling me with my nickname
        if isinstance(bot.config.NICKNAME, str) or not isinstance(bot.config.NICKNAME, Iterable):
            nicknames = (bot.config.NICKNAME,)
        else:
            nicknames = filter(lambda n: n, bot.config.NICKNAME)
        nickname_regex = '|'.join(nicknames)
        m = re.search(rf'^({nickname_regex})([\s,，]*|$)', first_text, re.IGNORECASE)
        if m:
            nickname = m.group(1)
            logger.debug(f'User is calling me {nickname}')
            ctx['to_me'] = True
            first_msg_seg.data['text'] = first_text[m.end():] or 'help'


def log_message(ctx: Context_T) -> None:
    msg_from: str = ctx['msg_sender_id']
    if ctx['msg_from_type'] == 'group':
        msg_from += f'@[Channel: {ctx["msg_group_id"]}]'
    logger.info(f'User: {msg_from}, '
                f'Message {ctx["msg_id"]} from {msg_from}: '
                f'{ctx["message"][0]}')
