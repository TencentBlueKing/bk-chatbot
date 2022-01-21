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

from typing import Optional, Callable, Union

from .proxy.bus import EventBus
from .adapter import Bot
from .session import BaseSession
from .self_typing import Context_T
from .log import logger

_bus = EventBus()


def _make_event_deco(post_type: str) -> Callable:
    def deco_deco(arg: Optional[Union[str, Callable]] = None,
                  *events: str) -> Callable:
        def deco(func: Callable) -> Callable:
            if isinstance(arg, str):
                for e in [arg] + list(events):
                    _bus.subscribe(f'{post_type}.{e}', func)
            else:
                _bus.subscribe(post_type, func)
            return func

        if isinstance(arg, Callable):
            return deco(arg)
        return deco

    return deco_deco


class EventSession(BaseSession):
    __slots__ = ()

    def __init__(self, bot: Bot, ctx: Context_T):
        super().__init__(bot, ctx)


on_event_click = _make_event_deco('Event.click')
on_event_enter_chat = _make_event_deco('Event.enter_chat')


async def handle_event(bot: Bot, ctx: Context_T) -> None:
    """
    todo parse detailed_type, classify and deal
    """
    post_type = ctx.get('msg_type')
    detailed_type = ctx.get('event')
    event = f"{post_type}.{detailed_type}"

    _log_event(ctx)
    session = EventSession(bot, ctx)

    logger.debug(f'Emitting event: {event}')
    try:
        await _bus.emit(event, session)
    except Exception as e:
        logger.error(f'An exception occurred while handling event {event}:')
        logger.exception(e)


@on_event_click
async def _(session: EventSession) -> bool:
    """
    Handle Event.click method
    This method will parse the key, then do distribute
    """
    return True


@on_event_enter_chat
async def _(session: EventSession) -> bool:
    """
    Handle Event.enter_chat method
    This method will judge user, then send tips
    """
    return True


def _log_event(ctx: Context_T) -> None:
    logger.info(f'Event: {ctx}')
