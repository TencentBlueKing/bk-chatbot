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
from .api import JobTask
from .settings import (
    JOB_PLAN_LIST_KEY, JOB_PLAN_LIST_ALIAS,
    JOB_PLAN_LIST_SORT_KEY, JOB_PLAN_SEARCH_KEY,
    JOB_PLAN_SELECT_KEY, JOB_PLAN_EXECUTE_KEY,
    JOB_PLAN_UPDATE_KEY, JOB_PLAN_CANCEL_KEY,
    JOB_PLAN_PARAM_PROMPT, JOB_PLAN_FORMAT_PROMPT,
    JOB_PLAN_CANCEL_TIP, JOB_PLAN_COMMON_PREFIX
)


@on_command(JOB_PLAN_LIST_KEY, aliases=JOB_PLAN_LIST_ALIAS)
async def list_job_plan(session: CommandSession):
    bk_biz_id = session.bot.parse_action('parse_select', session.ctx)
    job_task = JobTask(session, bk_biz_id)
    msg_template = await job_task.render_job_plan_list()
    if not msg_template:
        msg_template = job_task.render_null_msg('JOB')
    await session.send(**msg_template)


@on_command(JOB_PLAN_LIST_SORT_KEY)
async def sort_job_plan(session: CommandSession):
    pass


@on_command(JOB_PLAN_SEARCH_KEY)
async def search_job_plan(session: CommandSession):
    pass


@on_command(JOB_PLAN_SELECT_KEY)
async def select_bk_job_plan(session: CommandSession):
    msg_template = await JobTask(session).render_job_plan_detail()
    if msg_template:
        await session.send(**msg_template)


@on_command(JOB_PLAN_EXECUTE_KEY)
async def _(session: CommandSession):
    job_plan = session.bot.parse_action('parse_interaction', session.ctx)
    if not job_plan:
        return
    flow = JobTask(session)
    result = await flow.execute_task(job_plan)
    msg_template = flow.render_job_execute_msg(result, job_plan)
    await session.send(**msg_template)


@on_command(JOB_PLAN_UPDATE_KEY)
async def _(session: CommandSession):
    job_plan = session.bot.parse_action('parse_interaction', session.ctx)
    if not job_plan:
        return
    session.state.update(job_plan)
    title = '<bold>JOB TIP<bold>'
    content = f'{JOB_PLAN_PARAM_PROMPT}，<bold>{JOB_PLAN_FORMAT_PROMPT}<bold>'
    msg_template = session.bot.send_template_msg('render_markdown_msg', title, content)
    params, _ = session.get('params', prompt='...', **msg_template)
    params = params.split('\n')
    for i, item in enumerate(params):
        session.state['global_var_list'][i]['value'] = item

    msg_template = await JobTask(session).render_job_plan_detail()
    if msg_template:
        await session.send(**msg_template)


@on_command(JOB_PLAN_CANCEL_KEY)
async def _(session: CommandSession):
    bk_job_plan_name = session.bot.parse_action('parse_interaction', session.ctx)
    if not bk_job_plan_name:
        return
    title = '<bold>JOB TIP<bold>'
    content = f'<warning>{JOB_PLAN_COMMON_PREFIX}「{bk_job_plan_name}」{JOB_PLAN_CANCEL_TIP}...<warning>'
    msg_template = session.bot.send_template_msg('render_markdown_msg', title, content)
    await session.send(**msg_template)
