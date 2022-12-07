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
from .api import SopsTask


@on_command('bk_sops_template_list', aliases=('标准运维', 'sops', 'bk_sops'))
async def list_sops_template(session: CommandSession):
    bk_biz_id = session.bot.parse_action('parse_select', session.ctx)
    sops_task = SopsTask(session, bk_biz_id)
    msg_template = await sops_task.render_sops_template_list()
    if not msg_template:
        msg_template = sops_task.render_null_msg('SOPS')
    await session.send(**msg_template)


@on_command('bk_sops_template_select')
async def select_sops_template(session: CommandSession):
    msg_template = await SopsTask(session).render_sops_template_info()
    if msg_template:
        await session.send(**msg_template)


@on_command('bk_sops_template_execute')
async def execute_sops_template(session: CommandSession):
    bk_sops_template = session.bot.parse_action('parse_interaction', session.ctx)
    flow = SopsTask(session)
    result = await flow.execute_task(bk_sops_template)
    msg_template = flow.render_sops_execute_msg(result, bk_sops_template)
    await session.send(**msg_template)


@on_command('bk_sops_template_update')
async def update_sops_template(session: CommandSession):
    bk_sops_template = session.bot.parse_action('parse_interaction', session.ctx)
    if bk_sops_template:
        session.state['bk_sops_template'] = bk_sops_template
    msg_template = session.bot.send_template_msg('render_markdown_msg',
                                                 '<bold>SOPS TIP<bold>',
                                                 '请顺序输入参数，<bold>换行分隔<bold>')
    params, _ = session.get('params', prompt='...', **msg_template)
    params = params.split('\n')
    for i, item in enumerate(params):
        session.state['bk_sops_template']['constants'][i]['value'] = item

    msg_template = await SopsTask(session).render_sops_template_info()
    if msg_template:
        await session.send(**msg_template)


@on_command('bk_sops_template_cancel')
async def _(session: CommandSession):
    bk_sops_template_name = session.bot.parse_action('parse_interaction', session.ctx)
    msg_template = session.bot.send_template_msg('render_markdown_msg', '<bold>SOPS TIP<bold>',
                                                 f'<warning>您的标准运维任务「{bk_sops_template_name}」已取消...<warning>')
    await session.send(**msg_template)
