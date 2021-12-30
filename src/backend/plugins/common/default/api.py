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

import time, json
from typing import List, Callable

from opsbot import CommandSession
from component import RedisClient, CC, Backend, Plugin
from .settings import (
    DEFAULT_WELCOME_MSG, DEFAULT_WELCOME_BIZ, DEFAULT_WELCOME_REBIND,
    DEFAULT_WELCOME_BIND, DEFAULT_WELCOME_INTENT, DEFAULT_INTENT_CATEGORY, DEFAULT_BIZ_TIP,
    DEFAULT_WELCOME_TIP, DEFAULT_TOOL_BAR, DEFAULT_TOOL_EXTRA, DEFAULT_GUIDE_URL
)


def is_cache_visit(user_id: str, redis_client: RedisClient) -> bool:
    key = f'enter_chat_{user_id}'
    is_exist = redis_client.get(key)
    if is_exist:
        return True

    redis_client.set(key, json.dumps({'timestamp': time.time()}), ex=7200)
    return False


async def render_welcome_msg(session: CommandSession, redis_client: RedisClient) -> List:
    user_id = session.ctx['msg_sender_id']
    rich_text = [
        {'text': {'content': DEFAULT_WELCOME_MSG.format(user=user_id, name=session.bot.config.RTX_NAME)},
         'type': 'text'}
    ]

    if session.ctx['msg_from_type'] == 'single':
        biz_id = redis_client.hash_get("chat_single_biz", user_id)
    else:
        biz_id = redis_client.hash_get("chat_group_biz", session.ctx['msg_group_id'])

    biz_name = ''
    if not biz_id or str(biz_id) == '-1':
        biz_id = '-1'
        rich_text.append({'text': {'content': DEFAULT_WELCOME_BIND}, 'type': 'text'})
    else:
        response = await CC().search_business(bk_username=user_id, condition={'bk_biz_id': int(biz_id)})
        data = response.get('info')
        if data:
            biz_name = data[0]["bk_biz_name"]
            rich_text.append({
                'text': {'content': f'{DEFAULT_WELCOME_BIZ}【{biz_name}】 {DEFAULT_WELCOME_REBIND}'},
                'type': 'text'})
    rich_text.append({'type': 'link', 'link': {'text': '设置业务\n', 'type': 'click', 'key': 'biz_list'}})

    if DEFAULT_INTENT_CATEGORY:
        rich_text.append({'text': {'content': f'{DEFAULT_WELCOME_TIP}'}, 'type': 'text'})
        rich_text.append({'link': {'text': 'IWIKI\n', 'key': f'{DEFAULT_GUIDE_URL}', 'type': 'view'}, 'type': 'link'})
        rich_text.append({'type': 'text', 'text': {'content': f'-------------------\n'}})
        rich_text.extend(await render_default_intent(session, lambda x: x['key'] not in DEFAULT_INTENT_CATEGORY))
        rich_text.append({'type': 'text', 'text': {'content': f'-------------------\n'}})

    if DEFAULT_TOOL_EXTRA:
        rich_text.extend(render_tool_bar(biz_name, biz_id, user_id, DEFAULT_TOOL_EXTRA))

    if DEFAULT_TOOL_BAR:
        rich_text.extend(render_tool_bar(biz_name, biz_id, user_id, DEFAULT_TOOL_BAR))

    return rich_text


async def render_biz_msg(user_id: str) -> List:
    response = await CC().search_business(bk_username=user_id, fields=["bk_biz_id", "bk_biz_name"])
    rich_text = [{'text': {'content': f'{DEFAULT_BIZ_TIP}\n'}, 'type': 'text'}]
    for i, item in enumerate(response.get('info')):
        rich_text.append({'type': 'link', 'link': {'text': f'【{item["bk_biz_name"]}】,', 'type': 'click',
                                                   'key': f'bind_biz|{item["bk_biz_id"]}|{user_id}'}})
        if (i + 1) % 4 == 0:
            rich_text.append({'text': {'content': '\n'}, 'type': 'text'})

    return rich_text


async def render_default_intent(session: CommandSession, condition: Callable) -> List:
    if session.bot.type != 'in_xwork':
        return []

    rich_text = []
    for i, item in enumerate(DEFAULT_WELCOME_INTENT):
        if condition(item):
            continue

        rich_text.append({'type': 'text', 'text': {'content': f'* {item["name"]}\n'}})
        if item['key'] == 'operation':
            plugins = await Plugin(version='v2').list(tag=item['name'])
            plugins = [{'key': item['key'], 'text': item['name'], 'url': item['url']} for item in plugins]
            plugins.extend(item['detail'])
        else:
            plugins = item['detail']

        for plugin in plugins:
            if plugin.get('url'):
                rich_text.append({'type': 'link', 'link': {'text': f'【{plugin["text"]}】 ',
                                  'type': 'view', 'key': plugin['url'], 'browser': 0}})
            else:
                rich_text.append({'type': 'link', 'link': {'text': f'【{plugin["text"]}】 ',
                                  'type': 'click', 'key': plugin['key']}})
            if plugin == plugins[-1]:
                rich_text.append({'type': 'text', 'text': {'content': '\n'}})
            else:
                rich_text.append({'type': 'text', 'text': {'content': ', '}})

    return rich_text


def render_tool_bar(biz_name: str, biz_id: int, user_id: str, config: List) -> List:
    rich_text = []
    for item in config:
        rich_text.append({'type': 'text', 'text': {'content': item['content']}})
        operation = {'text': item['text'], 'type': item['type'], 'key': item['key'](biz_name, biz_id, user_id)}
        if item['type'] == 'view':
            operation['browser'] = item['browser']
        rich_text.append({'type': 'link', 'link': operation})

    return rich_text


async def bind_group_biz(group_id: str, biz_id: int, bot_type: str='xwork'):
    return await Backend().chat_bind(chat_group_id=group_id, chat_bot_type=bot_type, biz_id=biz_id,
                                     biz_name='-', chat_group_name='-')
