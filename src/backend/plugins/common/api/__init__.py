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

import json

from opsbot import on_command, CommandSession
from opsbot.log import logger

from .api import DispatchMSG


@on_command('send_msg', aliases=('send_msg',))
async def _(session: CommandSession):
    try:
        await session.send(**session.ctx['payload'])
    except KeyError:
        logger.exception(f'API ERROR {session.ctx}')


@on_command('dispatch_msg', aliases=('dispatch_msg',))
async def _(session: CommandSession):
    dispatcher = DispatchMSG(session)
    if 'event_key' in session.ctx:
        _, option, callback = session.ctx['event_key'].split('|')
        if dispatcher.is_exist(callback):
            return
        try:
            callback = json.loads(callback)
        except json.decoder.JSONDecodeError:
            logger.error(f'PARAMS PARSE ERROR: {session.ctx}')
            return
        msg = await getattr(dispatcher, f'handle_{option}')(callback)
        await session.send(msg)
    else:
        payload = dispatcher.process_msg()
        await session.send(**payload)
