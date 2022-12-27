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


@on_command('bk_chat_stat_execution', aliases=('执行统计', ))
@on_admin
async def _(session: CommandSession):
    stat = Stat()
    count = stat.stat_execution()
    title = '<bold>执行统计<bold>'
    content = f'<warning>您当前执行数「{count}」<warning>'
    msg_template = session.bot.send_template_msg('render_markdown_msg', title, content)
    await session.send(**msg_template)
    del stat