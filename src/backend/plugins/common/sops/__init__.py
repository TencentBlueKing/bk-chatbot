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
from .api import SopsTask


@on_command('bk_sops_template_list', aliases=('标准运维', 'sops', 'bk_sops'))
async def list_sops_template(session: CommandSession):
    try:
        bk_biz_id = session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
    except KeyError:
        bk_biz_id = None

    msg_template = await SopsTask(session, bk_biz_id).render_sops_template_list()
    if msg_template:
        await session.send(**msg_template)


@on_command('bk_sops_template_select')
async def select_sops_template(session: CommandSession):
    msg_template = await SopsTask(session).render_sops_template_info()
    if msg_template:
        await session.send(**msg_template)


@on_command('bk_sops_template_execute')
async def execute_sops_template(session: CommandSession):
    _, bk_sops_template = session.ctx['event_key'].split('|')
    bk_sops_template = json.loads(bk_sops_template)

    flow = SopsTask(session)
    result = await flow.execute_task(bk_sops_template)
    msg_template = flow.render_sops_execute_msg(result, bk_sops_template)
    await session.send(**msg_template)


@on_command('bk_sops_template_update')
async def update_sops_template(session: CommandSession):
    if 'event_key' in session.ctx:
        _, bk_sops_template = session.ctx['event_key'].split('|')
        session.state['bk_sops_template'] = json.loads(bk_sops_template)

    content = f'''>**SOPS TIP**
        >请顺序输入参数，**换行分隔**'''
    msg_template = session.bot.send_template_msg('render_markdown_msg', content)
    params, _ = session.get('params', prompt='...', **msg_template)
    params = params.split('\n')
    for i, item in enumerate(params):
        session.state['bk_sops_template']['constants'][i]['value'] = item

    msg_template = await SopsTask(session).render_sops_template_info()
    if msg_template:
        await session.send(**msg_template)


@on_command('bk_sops_template_cancel')
async def _(session: CommandSession):
    _, bk_sops_template_name = session.ctx['event_key'].split('|')
    msg_template = session.bot.send_template_msg('render_task_cancel_msg', 'SOPS',
                                                 f'您的标准运维任务「{bk_sops_template_name}」已取消...')
    await session.send(**msg_template)
