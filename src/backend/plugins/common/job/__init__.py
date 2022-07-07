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
from .api import JobTask


@on_command('bk_job_plan_list', aliases=('JOB任务', 'JOB执行方案', '作业平台', 'bk_job'))
async def list_job_plan(session: CommandSession):
    try:
        bk_biz_id = session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
    except KeyError:
        bk_biz_id = None

    msg_template = await JobTask(session, bk_biz_id).render_job_plan_list()
    if not msg_template:
        msg_template = render_null_msg('JOB')
    await session.send(**msg_template)


@on_command('bk_job_plan_sort')
async def sort_job_plan(session: CommandSession):
    pass


@on_command('bk_job_plan_search')
async def search_job_plan(session: CommandSession):
    pass


@on_command('bk_job_plan_select')
async def select_bk_job_plan(session: CommandSession):
    msg_template = await JobTask(session).render_job_plan_detail()
    if msg_template:
        await session.send(**msg_template)


@on_command('bk_job_plan_execute')
async def _(session: CommandSession):
    _, job_plan = session.ctx['event_key'].split('|')
    try:
        job_plan = json.loads(job_plan)
    except json.JSONDecodeError:
        return

    flow = JobTask(session)
    result = await flow.execute_task(job_plan)
    msg_template = flow.render_job_execute_msg(result, job_plan)
    await session.send(**msg_template)


@on_command('bk_job_plan_update')
async def _(session: CommandSession):
    if 'event_key' in session.ctx:
        _, job_plan = session.ctx['event_key'].split('|')
        try:
            job_plan = json.loads(job_plan)
        except json.JSONDecodeError:
            return
        session.state.update(job_plan)

    content = f'''>**JOB TIP**
    >请顺序输入参数，**换行分隔**'''
    msg_template = session.bot.send_template_msg('render_markdown_msg', content)
    params, _ = session.get('params', prompt='...', **msg_template)
    params = params.split('\n')
    for i, item in enumerate(params):
        session.state['global_var_list'][i]['value'] = item

    msg_template = await JobTask(session).render_job_plan_detail()
    if msg_template:
        await session.send(**msg_template)


@on_command('bk_job_plan_cancel')
async def _(session: CommandSession):
    _, bk_job_plan_name = session.ctx['event_key'].split('|')
    content = f'''>**JOB TIP** 
                ><font color=\"warning\">您的JOB执行方案「{bk_job_plan_name}」已取消...</font> 
                '''
    msg_template = session.bot.send_template_msg('render_markdown_msg', content)
    await session.send(**msg_template)
