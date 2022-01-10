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
from opsbot.log import logger

from .api import SopsTask


@on_command('bk_sops_template_list', aliases=('标准运维', 'sops', 'bk_sops'))
async def list_sops_template(session: CommandSession):
    try:
        bk_biz_id = session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
    except KeyError:
        bk_biz_id = None

    msg = await SopsTask(session, bk_biz_id).render_sops_template_list()
    if msg:
        await session.send('', msgtype='template_card', template_card=msg)


@on_command('bk_sops_template_select')
async def select_sops_template(session: CommandSession):
    msg = await SopsTask(session).render_sops_template_info()
    if msg:
        await session.send('', msgtype='template_card', template_card=msg)


@on_command('bk_sops_template_execute')
async def execute_sops_template(session: CommandSession):
    logger.info(session.ctx)


@on_command('bk_sops_template_update')
async def update_sops_template(session: CommandSession):
    pass


@on_command('bk_sops_template_cancel')
async def _(session: CommandSession):
    pass
