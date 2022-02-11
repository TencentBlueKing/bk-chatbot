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
from opsbot import on_natural_language, NLPSession, IntentCommand
from .api import ShortcutHandler


@on_command('bk_shortcut_create')
async def create_bk_shortcut(session: CommandSession):
    if 'event_key' in session.ctx:
        _, platform, info = session.ctx['event_key'].split('|')
        session.state['platform'] = platform
        session.state['info'] = json.loads(info)
    else:
        platform = session.state['platform']
        info = session.state['info']

    content = f'''>**{platform} TIP**
            >请输入快捷键名称，**最少输入8个字符**, 每个人每个业务最多10个快捷键'''
    shortcut_name, _ = session.get('shortcut_name', prompt='...', msgtype='markdown', markdown={'content': content})
    sc_handler = ShortcutHandler(session, shortcut_name)
    while not sc_handler.validate_name():
        del session.state['shortcut_name']
        shortcut_name, _ = session.get('shortcut_name', prompt='...', msgtype='markdown', markdown={'content': content})

    sc_handler.save(platform, info)
    content = f'''>**{platform} TIP**
                >快捷键「{shortcut_name}」保存成功'''
    await session.send('', msgtype='markdown', markdown={'content': content})


@on_command('bk_shortcut_execute')
async def execute_bk_shortcut(session: CommandSession):
    shortcut = session.state['info']
    sc_handler = ShortcutHandler(session)
    msg = await sc_handler.execute_task(shortcut)
    await session.send('', msgtype='template_card', template_card=msg)


@on_command('bk_shortcut_list')
async def list_bk_shortcut(session: CommandSession):
    msg = ShortcutHandler(session).render_shortcut_list()
    await session.send('', msgtype='template_card', template_card=msg)


@on_command('bk_shortcut_delete')
async def delete_bk_shortcut(session: CommandSession):
    sc_handler = ShortcutHandler(session)
    msg = sc_handler.delete()
    content = f'''>**快捷键 TIP**
                    >快捷键「{msg}」删除成功'''
    await session.send('', msgtype='markdown', markdown={'content': content})

@on_natural_language
async def _(session: NLPSession):
    msg = session.msg_text.strip()
    sc_handler = ShortcutHandler(session, msg)
    shortcut = sc_handler.find_one()
    if shortcut:
        return IntentCommand(100, 'bk_shortcut_execute', args={'info': shortcut})
