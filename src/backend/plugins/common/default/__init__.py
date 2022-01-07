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

from opsbot import on_command, CommandSession, on_natural_language
from opsbot.log import logger
from .api import (
    render_welcome_msg, render_biz_msg, render_default_intent, is_cache_visit,
    bind_group_biz, Flow
)
from .settings import (
    DEFAULT_SHOW_GROUP_ID_ALIAS, DEFAULT_BIND_BIZ_ALIAS, DEFAULT_BIND_BIZ_TIP,
    DEFAULT_BIZ_BIND_SUCCESS, DEFAULT_BIZ_BIND_FAIL, DEFAULT_HELPER, DEFAULT_INTENT_CATEGORY
)


@on_command('group_id', aliases=DEFAULT_SHOW_GROUP_ID_ALIAS)
async def _(session: CommandSession):
    if session.ctx['msg_from_type'] == 'group':
        await session.send(session.ctx['msg_group_id'])


@on_command('welcome', aliases=('help', '帮助', '小鲸', '1'))
async def _(session: CommandSession):
    if 'event_key' in session.ctx:
        return

    msg = await Flow(session).render_welcome_msg()
    await session.send('', msgtype='template_card', template_card=msg)


@on_command('bk_cc_biz_bind', aliases=DEFAULT_BIND_BIZ_ALIAS)
async def _(session: CommandSession):
    msg = await Flow(session).render_biz_msg()
    if msg:
        await session.send('', msgtype='template_card', template_card=msg)
    else:
        logger.info('no biz')


@on_command('bk_cc_biz_select')
async def _(session: CommandSession):
    flow = Flow(session)
    bk_biz_id = flow.bind_cc_biz()
    if not bk_biz_id:
        logger.info('bind biz error')
        return

    msg = await flow.render_welcome_msg()
    await session.send('', msgtype='template_card', template_card=msg)

