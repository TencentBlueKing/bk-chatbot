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

from opsbot import on_command, CommandSession
from opsbot import on_natural_language, NLPSession, IntentCommand
from .api import ShortcutHandler
from .settings import (
    SHORTCUT_CREATE_KEY, SHORTCUT_EXECUTE_KEY, SHORTCUT_LIST_KEY,
    SHORTCUT_LIST_ALIAS, SHORTCUT_DELETE_KEY, SHORTCUT_COMMON_LABEL,
    SHORTCUT_NAME_INPUT_PREFIX, SHORTCUT_NAME_FORMAT_TIP,
    SHORTCUT_SAVE_TIP, SHORTCUT_NULL_TIP, SHORTCUT_DELETE_TIP
)


@on_command(SHORTCUT_CREATE_KEY)
async def create_bk_shortcut(session: CommandSession):
    info = session.bot.parse_action('parse_interaction', session.ctx)
    if info is None:
        platform = session.state['platform']
        info = session.state['info']
    else:
        platform = info.get('platform')
        session.state['platform'] = info.get('platform')
        session.state['info'] = info

    title = f'<bold>{platform} TIP<bold>'
    content = f'{SHORTCUT_NAME_INPUT_PREFIX}，<bold>{SHORTCUT_NAME_FORMAT_TIP}<bold>'
    msg_template = session.bot.send_template_msg('render_markdown_msg', title, content)
    shortcut_name, _ = session.get('shortcut_name', prompt='...', **msg_template)
    sc_handler = ShortcutHandler(session, shortcut_name)
    while not sc_handler.validate_name():
        del session.state['shortcut_name']
        shortcut_name, _ = session.get('shortcut_name', prompt='...', **msg_template)

    sc_handler.save(platform, info)
    content = f'{SHORTCUT_COMMON_LABEL}「{shortcut_name}」{SHORTCUT_SAVE_TIP}'
    msg_template = session.bot.send_template_msg('render_markdown_msg', title, content)
    await session.send(**msg_template)


@on_command(SHORTCUT_EXECUTE_KEY)
async def execute_bk_shortcut(session: CommandSession):
    shortcut = session.state['info']
    sc_handler = ShortcutHandler(session)
    msg_template = await sc_handler.execute_task(shortcut)
    msg_template and await session.send(**msg_template)


@on_command(SHORTCUT_LIST_KEY, aliases=SHORTCUT_LIST_ALIAS)
async def list_bk_shortcut(session: CommandSession):
    msg_template = ShortcutHandler(session).render_shortcut_list()
    if not msg_template:
        title = '<bold>BKCHAT TIP<bold>'
        content = SHORTCUT_NULL_TIP
        msg_template = session.bot.send_template_msg('render_markdown_msg', title, content)
    await session.send(**msg_template)


@on_command(SHORTCUT_DELETE_KEY)
async def delete_bk_shortcut(session: CommandSession):
    sc_handler = ShortcutHandler(session)
    msg = sc_handler.delete()
    title = f'<bold>{SHORTCUT_COMMON_LABEL} TIP<bold>'
    content = f'{SHORTCUT_COMMON_LABEL}「{msg}」{SHORTCUT_DELETE_TIP}'
    msg_template = session.bot.send_template_msg('render_markdown_msg', title, content)
    msg_template and await session.send(**msg_template)


@on_natural_language
async def _(session: NLPSession):
    msg = session.msg_text.strip()
    sc_handler = ShortcutHandler(session, msg)
    shortcut = sc_handler.find_one()
    if shortcut:
        return IntentCommand(100, SHORTCUT_EXECUTE_KEY, args={'info': shortcut})
