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

import base64
import json
import time
import urllib
import urllib.request, urllib.parse, urllib.error

import requests

from opsbot import (
    on_command, CommandSession, on_natural_language, NLPSession
)
from opsbot.log import logger
from opsbot.proxy import (
    ApiError,
)
from opsbot.stdlib import Aes
from .settings import (
    PLUGIN_KEY, PLUGIN_INDEX_MSG, PLUGIN_INDEX_EXAMPLE, PLUGIN_PARAMS_TEMPLATE,
    PLUGIN_PARAMS_MAP, PLUGIN_ACTION, ITSM_KEY, ITSM_KEYWORDS,
)
from .api import RuleParser, Ticket


@on_command('itsm_ticket_approved')
async def _(session: CommandSession):
    """单据审批"""
    current_user_id = session.ctx['msg_sender_id']

    if 'user_id' in session.state:
        ticket_id = session.state['ticket_id']
        app_id = session.state['app_id']
        app_key = session.state['app_key']
        callback_url = session.state['callback_url']
        action_value = session.state['action_value']
        context = session.state['context']
        # detail_url = session.state['detail_url']
        # plat_url = session.state['plat_url']
        # ticket_name = session.state['ticket_name']
        # user_id = session.state['user_id']
    else:
        _, action_value, ctx_msg = session.ctx['event_key'].split('|', maxsplit=2)
        ticket_id, context, ticket_name, plat_url, callback_url, detail_url, app_id, app_key = ctx_msg.split('|')
        session.state['user_id'] = current_user_id
        session.state['ticket_id'] = ticket_id
        session.state['ticket_name'] = ticket_name
        session.state['app_id'] = app_id
        session.state['app_key'] = app_key
        session.state['callback_url'] = callback_url
        session.state['plat_url'] = plat_url
        session.state['detail_url'] = detail_url
        session.state['action_value'] = action_value
        session.state['context'] = context

    try:
        context = json.loads(base64.b64decode(context))
        callback_url = urllib.parse.unquote(callback_url)
        data = {
            'key': ticket_id,
            'context': context,
            'status': action_value,
            'approver': current_user_id,
            'time': round(time.time()),
        }
        encrypt_msg = Aes(app_id, app_key).encrypt_dict(data)
        resp = requests.post(callback_url, data=encrypt_msg, verify=False).json()
        rich_text = [
            {'text': {'content': resp.get('message', '第三方系统返回为空')}, 'type': 'text'},
        ]
        await session.send('', msgtype='rich_text', rich_text=rich_text)
    except requests.exceptions.RequestException as e:
        msg = f'单号：{ticket_id} 审批异常，第三方系统请求异常'
        logger.error(f'{msg}: {e}')
        await session.send('', msgtype='rich_text', rich_text=[
            {'text': {'content': msg}, 'type': 'text'},
        ])
        raise ApiError(f'HTTP request failed with exception {e}')
    except (TypeError, AttributeError) as e:
        msg = f'单号：{ticket_id}, 审批异常：{e}'
        logger.error(msg)
        await session.send('', msgtype='rich_text', rich_text=[
            {'text': {'content': msg}, 'type': 'text'},
        ])
        raise ApiError(f'Command <itsm_ticket_approved> exception {e}')


@on_command('itsm_ticket_created')
async def _(session: CommandSession):
    """创建单据"""
    pass


@on_command('COMMON_PLUGIN_ITSM_DAEMON')
async def _(session: CommandSession):
    ticket = Ticket(session)
    if 'event_key' in session.ctx:
        _, option, group_id, sender, biz_name, biz_id, content = session.ctx['event_key'].split('|')
        if await ticket.is_exist(biz_id, group_id, sender, content):
            return

        await getattr(ticket, option)(biz_id, biz_name, content, group_id, sender)
    else:
        biz_id = session.state.get('biz_id')
        receiver = session.state.get('receiver')
        content = session.state.get('content')
        await ticket.send(biz_id, content, receiver)


@on_command('COMMON_PLUGIN_ITSM_SELF')
async def _(session: CommandSession):
    biz_id = session.state.get('biz_id')
    receiver = session.state.get('receiver')
    content = session.state.get('content')

    ticket = Ticket(session)
    biz = await ticket.get_biz(bk_biz_id=int(biz_id), bk_biz_maintainer=receiver)
    if biz:
        biz_name = biz["bk_biz_name"]
        await ticket.create(biz_id, biz_name, content, session.ctx['msg_group_id'], receiver)


@on_natural_language(only_to_me=False)
async def _(session: NLPSession):
    if session.ctx['msg_from_type'] == 'group' and session.bot.config.ID == 'BKCHAT':
        return await RuleParser(session).evaluate()
