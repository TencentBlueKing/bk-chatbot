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

from .api import Stat, on_admin
from .settings import (
    ADMIN_STAT_EXECUTION_KEY, ADMIN_STAT_EXECUTION_ALIAS,
    ADMIN_STAT_EXECUTION_TITLE, ADMIN_STAT_EXECUTION_PREFIX
)


@on_command(ADMIN_STAT_EXECUTION_KEY, aliases=ADMIN_STAT_EXECUTION_ALIAS)
@on_admin
async def _(session: CommandSession):
    stat = Stat()
    count = stat.stat_execution()
    title = f'<bold>{ADMIN_STAT_EXECUTION_TITLE}<bold>'
    content = f'<warning>{ADMIN_STAT_EXECUTION_PREFIX}「{count}」<warning>'
    msg_template = session.bot.send_template_msg('render_markdown_msg', title, content)
    await session.send(**msg_template)
    del stat
