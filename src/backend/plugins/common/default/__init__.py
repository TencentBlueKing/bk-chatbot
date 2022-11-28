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
from .api import Flow, Stat
from .settings import (
    DEFAULT_SHOW_GROUP_ID_ALIAS, DEFAULT_BIND_BIZ_ALIAS, DEFAULT_BIND_BIZ_TIP,
    DEFAULT_BIZ_BIND_SUCCESS, DEFAULT_BIZ_BIND_FAIL, DEFAULT_HELPER, DEFAULT_INTENT_CATEGORY
)


@on_command('bk_chat_group_id', aliases=DEFAULT_SHOW_GROUP_ID_ALIAS)
async def _(session: CommandSession):
    if session.ctx['msg_from_type'] == 'group':
        await session.send(session.ctx['msg_group_id'])


@on_command('bk_chat_welcome', aliases=('help', '帮助', '小鲸', '1'))
async def _(session: CommandSession):
    if 'event_key' in session.ctx:
        return

    msg_template = await Flow(session).render_welcome_msg()
    await session.send(**msg_template)


@on_command('bk_env_bind')
async def _(session: CommandSession):
    pass


@on_command('bk_cc_biz_bind', aliases=DEFAULT_BIND_BIZ_ALIAS)
async def _(session: CommandSession):
    msg_template = await Flow(session).render_biz_msg()
    if msg_template:
        await session.send(**msg_template)
    else:
        logger.info('no biz')


@on_command('bk_cc_biz_select')
async def _(session: CommandSession):
    flow = Flow(session)
    bk_biz_id = flow.bind_cc_biz()
    if not bk_biz_id:
        logger.info('bind biz error')
        return

    msg_template = await flow.render_welcome_msg()
    await session.send(**msg_template)


@on_command('bk_chat_stat_execution', aliases=('执行统计', ))
async def _(session: CommandSession):
    stat = Stat()
    count = stat.stat_execution()
    content = f'''>**执行统计** 
                ><font color=\"warning\">您当前执行数「{count}」</font> 
                '''
    msg_template = session.bot.send_template_msg('render_markdown_msg', content)
    await session.send(**msg_template)
    del stat


@on_command('bk_chat_search_knowledge')
async def _(session: CommandSession):
    answers = session.state.get('answers')
    content = '\n'.join([
        f'''><font color=\"info\">问题：{item["question"]}</font>
        ><font color=\"warning\">答案：{item["solution"]}</font>'''
        for item in answers
    ])
    content = f'''>**结果:**\n{content}'''
    msg_template = session.bot.send_template_msg('render_markdown_msg', content)
    await session.send(**msg_template)


@on_natural_language
async def _(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    command = await SelfPrediction(session).run(stripped_msg)
    if command:
        return IntentCommand(*command[:2], args=command[2])

    answers = fetch_answer(stripped_msg)
    if answers:
        return IntentCommand(100, 'bk_chat_search_knowledge', args={'answers': answers})
