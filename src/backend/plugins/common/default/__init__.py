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

from opsbot import (
    on_command, on_natural_language, IntentCommand,
    NLPSession, CommandSession
)
from opsbot.log import logger
from component import fetch_answer
from plugins.common.task import Prediction as SelfPrediction
from .api import Flow
from .settings import (
    DEFAULT_SHOW_GROUP_ID_ALIAS, DEFAULT_BIND_BIZ_ALIAS,
    DEFAULT_QUERY_CHAT_KEY, DEFAULT_WELCOME_KEY,
    DEFAULT_BIND_ENV_KEY, DEFAULT_BIND_BIZ_KEY,
    DEFAULT_SELECT_BIZ_KEY, DEFAULT_SEARCH_QA_KEY,
    DEFAULT_HANDLE_CALLBACK_KEY, DEFAULT_SEARCH_QA_RESULT,
    DEFAULT_SEARCH_QA_QUESTION, DEFAULT_SEARCH_QA_ANSWER
)


@on_command(DEFAULT_QUERY_CHAT_KEY, aliases=DEFAULT_SHOW_GROUP_ID_ALIAS)
async def _(session: CommandSession):
    if session.ctx['msg_from_type'] == 'group':
        await session.send(session.ctx['msg_group_id'])


@on_command(DEFAULT_WELCOME_KEY, aliases=('help', '帮助', '小鲸', '1'))
async def _(session: CommandSession):
    info = session.bot.parse_action('parse_interaction', session.ctx)
    if info is not None:
        return
    msg_template = await Flow(session).render_welcome_msg()
    await session.send(**msg_template)


@on_command(DEFAULT_BIND_ENV_KEY)
async def _(session: CommandSession):
    pass


@on_command(DEFAULT_BIND_BIZ_KEY, aliases=DEFAULT_BIND_BIZ_ALIAS)
async def _(session: CommandSession):
    msg_template = await Flow(session).render_biz_msg()
    if msg_template:
        await session.send(**msg_template)
    else:
        logger.info('no biz')


@on_command(DEFAULT_SELECT_BIZ_KEY)
async def _(session: CommandSession):
    flow = Flow(session)
    bk_biz_id = flow.bind_cc_biz()
    if not bk_biz_id:
        logger.info('bind biz error')
        return

    msg_template = await flow.render_welcome_msg()
    await session.send(**msg_template)


@on_command(DEFAULT_SEARCH_QA_KEY)
async def _(session: CommandSession):
    answers = session.state.get('answers')
    title = f'<bold>{DEFAULT_SEARCH_QA_RESULT}:<bold>'
    content = '\n'.join([
        f'''<info>{DEFAULT_SEARCH_QA_QUESTION}：{item["question"]}<info>
        <warning>{DEFAULT_SEARCH_QA_ANSWER}：{item["solution"]}<warning>'''
        for item in answers
    ])
    msg_template = session.bot.send_template_msg('render_markdown_msg', title, content)
    await session.send(**msg_template)


@on_command(DEFAULT_HANDLE_CALLBACK_KEY)
async def _(session: CommandSession):
    pass


@on_natural_language
async def _(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    command = await SelfPrediction(session).run(stripped_msg)
    if command:
        return IntentCommand(*command[:2], args=command[2])

    answers = fetch_answer(stripped_msg)
    if answers:
        return IntentCommand(100, 'bk_chat_search_knowledge', args={'answers': answers})
