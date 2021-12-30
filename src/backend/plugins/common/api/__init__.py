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
import urllib

from opsbot import on_command, CommandSession
from opsbot.exceptions import ApiError
from opsbot.log import logger

from .api import DispatchMSG


@on_command('send_msg', aliases=('send_msg',))
async def _(session: CommandSession):
    try:
        await session.send('', **session.ctx['payload'])
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
        await session.send('', **payload)


@on_command('send_ticket', aliases=('send_ticket',))
async def _(session: CommandSession):
    """
    payload = {
        'app_id': 'test',
        'app_key': 'test',
        'data': {
            "title": "this is test title",
            "summary": "this is a test msg",
            "approvers": "gaomugong",
            "key": "SN12312323453223",

            "plat": "http://wwww.tst.com",
            "clickurl": "http://xx.com/detail",
            "clickname": "detail",
            "callback": "http://xxx/test/callback",
            "context" : {"key1": "v1", "key2": "v2"},
            "action": [
                {"name1": "yes", "value": "1"},
                {"name": "no", "value": "-1"}
            ]
        }
    }

    """

    payload = session.ctx['payload']

    app_id = payload['app_id']
    app_key = payload['app_key']
    data = payload['data']

    key = data['key']
    title = data['title']
    summary = data['summary']
    context = data.get('context', {})
    approvers = data['approvers']

    logger.info(f'send_ticket: app_id={app_id} app_key={app_key} data={data}')

    try:
        # 审批人为空
        approvers = [user_id for user_id in approvers.split(',') if user_id]
        if not approvers:
            logger.info('skip empty approvers ticket')
            return

        context = base64.b64encode(json.dumps(context).encode()).decode()
        plat_url = urllib.parse.quote(data.get('plat', ''))
        callback_url = urllib.parse.quote(data.get('callback', ''))
        detail_url = urllib.parse.quote(data.get('clickurl', ''))

    except Exception as e:
        logger.exception(f'API ERROR {session.ctx}')
        raise ApiError(f'command->send_ticket exception: {e}')

    # 标题\n正文\n
    rich_text = [
        {'text': {'content': title}, 'type': 'text'},
        {'text': {'content': '\n'}, 'type': 'text'},
        {'text': {'content': summary}, 'type': 'text'},
        {'text': {'content': '\n'}, 'type': 'text'},
    ]

    # 可选，单据操作
    for link in data.get('action', []):
        ctx_msg = f'{key}|{context}|{title}|{plat_url}|{callback_url}|{detail_url}|{app_id}|{app_key}'
        rich_text.extend(
            [
                {
                    'type': 'link',
                    'link': {
                        'text': f"{link['name']}\t\t\t",
                        'type': 'click',
                        'key': f"itsm_ticket_approved|{link['value']}|{ctx_msg}",
                    },
                }
            ]
        )

    # 可选，单据详情
    if data.get('clickurl'):
        rich_text.extend(
            [
                {
                    "type": "link",
                    "link": {"type": "view", "text": f"{data['clickname']}", "key": data['clickurl'], "browser": 1},
                }
            ]
        )

    for user_id in approvers:
        await session.send('', msgtype='rich_text', rich_text=rich_text, receiver={'type': 'single', 'id': user_id})

    session.state.clear()
