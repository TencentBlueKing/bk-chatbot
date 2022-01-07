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

from .api import Flow


@on_command('bk_job_plan_list', aliases=('JOB任务', 'JOB执行方案', ))
async def list_job_plan(session: CommandSession):
    msg = await Flow(session).render_job_plan_list()
    if msg:
        await session.send('', msgtype='template_card', template_card=msg)


@on_command('bk_job_plan_sort')
async def sort_job_plan(session: CommandSession):
    pass


@on_command('bk_job_plan_search')
async def search_job_plan(session: CommandSession):
    pass


@on_command('bk_job_plan_select')
async def select_bk_job_plan(session: CommandSession):
    logger.info(session.ctx)
    msg = await Flow(session).render_job_plan_detail()
    if msg:
        await session.send('', msgtype='template_card', template_card=msg)
