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
import asyncio
from typing import Callable

from xhttp.message import *
from . import OpsBot
from .self_typing import Context_T
from .log import logger
from .command import handle_command, SwitchException
from .natural_language import handle_natural_language

_message_preprocessors = set()


def message_preprocessor(func: Callable) -> Callable:
    _message_preprocessors.add(func)
    return func


async def handle_message(bot: OpsBot, ctx: Context_T) -> None:
    _log_message(ctx)

    if not ctx['message']:
        ctx['message'].append(MessageSegment.text(''))

    cor_os = []
    for processor in _message_preprocessors:
        cor_os.append(processor(bot, ctx))
    if cor_os:
        await asyncio.wait(cor_os)

    raw_to_me = ctx.get('to_me', False)
    _check_at_me(bot, ctx)
    _check_calling_me_nickname(bot, ctx)
    ctx['to_me'] = raw_to_me or ctx['to_me']

    while True:
        try:
            handled = await handle_command(bot, ctx)
            break
        except SwitchException as e:
            # we are sure that there is no session existing now
            ctx['message'] = e.new_ctx_message
            ctx['to_me'] = True
    if handled:
        logger.info(f'Message {ctx["MsgId"]} is handled as a command')
        return

    handled = await handle_natural_language(bot, ctx)
    if handled:
        logger.info(f'Message {ctx["MsgId"]} is handled '
                    f'as natural language')
        return


def _check_at_me(bot: OpsBot, ctx: Context_T) -> None:
    ctx['to_me'] = True


def _check_calling_me_nickname(bot: OpsBot, ctx: Context_T) -> None:
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
            first_msg_seg.data['text'] = first_text[m.end():]


def _log_message(ctx: Context_T) -> None:
    msg_from: str = ctx['FromUserName']
    logger.info(f'Self: {msg_from}, '
                f'Message {ctx["MsgId"]} from {msg_from}: '
                f'{ctx["Content"]}')
