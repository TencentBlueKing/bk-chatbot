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
    on_command, CommandSession,
)
from .api import GenericIT
from .settings import (
    ITSM_CHECK_SERVICE_KEY, ITSM_CHECK_SERVICE_KEY,
    ITSM_SELECT_SERVICE_KEY
)


@on_command(ITSM_CHECK_SERVICE_KEY, aliases=ITSM_CHECK_SERVICE_KEY)
async def _(session: CommandSession):
    msg = await GenericIT(session).render_services()
    msg and await session.send('', msgtype='template_card', template_card=msg)


@on_command(ITSM_SELECT_SERVICE_KEY)
async def _(session: CommandSession):
    msg = await GenericIT(session).render_service_detail()
    msg and await session.send('', msgtype='template_card', template_card=msg)
