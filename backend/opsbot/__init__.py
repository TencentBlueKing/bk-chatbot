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
import logging
from typing import Any, Optional

import xhttp.message
from xhttp import XWorkHttp

from .log import logger
from .sched import Scheduler

if Scheduler:
    scheduler = Scheduler()
else:
    scheduler = None


class OpsBot(XWorkHttp):
    def __init__(self, config_object: Optional[Any] = None):
        if config_object is None:
            from . import default_config as config_object

        config_dict = {k: v for k, v in config_object.__dict__.items()
                       if k.isupper() and not k.startswith('_')}
        logger.debug(f'Loaded configurations: {config_dict}')
        super().__init__(message_class=xhttp.message.Message,
                         **{k.lower(): v for k, v in config_dict.items()})

        self.config = config_object
        self.asgi.debug = self.config.DEBUG

        from .message import handle_message
        from .event import handle_event

        @self.on_text
        async def _(ctx):
            asyncio.ensure_future(handle_message(self, ctx))

        @self.on_event
        async def _(ctx):
            asyncio.ensure_future(handle_event(self, ctx))

    def run(self, host: Optional[str] = None, port: Optional[int] = None,
            *args, **kwargs) -> None:
        host = host or self.config.HOST
        port = port or self.config.PORT
        if 'debug' not in kwargs:
            kwargs['debug'] = self.config.DEBUG

        logger.info(f'Running on {host}:{port}')
        super().run(host=host, port=port, *args, **kwargs)


_bot: Optional[OpsBot] = None


def init(config_object: Optional[Any] = None) -> None:
    """
    Initialize OpsBot instance.

    This function must be called at the very beginning of code,
    otherwise the get_bot() function will return None and nothing
    is gonna work properly.

    :param config_object: configuration object
    """
    global _bot
    _bot = OpsBot(config_object)

    if _bot.config.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    _bot.server_app.before_serving(_start_scheduler)


def _start_scheduler():
    if scheduler and not scheduler.running:
        scheduler.configure(_bot.config.APSCHEDULER_CONFIG)
        scheduler.start()
        logger.info('Scheduler started')


def get_bot() -> OpsBot:
    """
    Get the OpsBot instance.

    The result is ensured to be not None, otherwise an exception will
    be raised.

    :raise ValueError: instance not initialized
    """
    if _bot is None:
        raise ValueError('OpsBot instance has not been initialized')
    return _bot


def run(host: Optional[str] = None, port: Optional[int] = None,
        *args, **kwargs) -> None:
    """
    Run the OpsBot instance.
    """
    get_bot().run(host=host, port=port, *args, **kwargs)


from .exceptions import *
from .plugin import (load_plugin, load_plugins, load_builtin_plugins,
                     get_loaded_plugins)
from .message import message_preprocessor, Message, MessageSegment
from .command import on_command, CommandSession, CommandGroup
from .natural_language import (on_natural_language, NLPSession, NLPResult,
                                IntentCommand)
from .event import EventSession
from .helpers import context_id

__all__ = [
    'OpsBot', 'scheduler', 'init', 'get_bot', 'run',

    'XWorkError',

    'load_plugin', 'load_plugins', 'load_builtin_plugins',
    'get_loaded_plugins',

    'message_preprocessor', 'Message', 'MessageSegment',

    'on_command', 'CommandSession', 'CommandGroup',

    'on_natural_language', 'NLPSession', 'NLPResult', 'IntentCommand',
    'EventSession',

    'context_id',
]
