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

from opsbot import CommandSession
from component import BKCloud
from .settings import (
    ITSM_WELCOME_TIP, ITSM_SERVICE_TEMPLATE_PREFIX,
    ITSM_ClICK_TIP
)


class GenericIT:
    def __init__(self, session: CommandSession, bk_env: str = 'v7'):
        self._session = session
        self.user_id = self._session.ctx['msg_sender_id']
        self._bk_service = BKCloud(bk_env).bk_service
        self._itsm = self._bk_service.itsm

    async def render_services(self):
        try:
            page = self._session.bot.parse_action('parse_interaction', self._session.ctx)
            page = int(page)
        except ValueError:
            return None

        services = await self._itsm.get_services()
        services = [{'id': str(var['id']), 'text': var['name']} for var in services]

        return self._session.bot.send_template_msg('render_ticket_service_list_msg',
                                                   'ITSM',
                                                   ITSM_WELCOME_TIP,
                                                   'bk_itsm'
                                                   'bk_itsm_service_id',
                                                   'bk_itsm_select_service',
                                                   services, page)

    async def render_service_detail(self):
        service_id = self._session.bot.parse_interaction('parse_select', self._session.ctx)
        if not service_id:
            return None

        service = await self._itsm.get_service_detail(service_id=int(service_id))
        return self._session.bot.send_template_msg('render_ticket_service_detail_msg',
                                                   'ITSM',
                                                   f'{ITSM_SERVICE_TEMPLATE_PREFIX}'
                                                   f'「{service["name"]}」{ITSM_ClICK_TIP}',
                                                   service,
                                                   f'{self._bk_service.BK_ITSM_DOMAIN}#/ticket/'
                                                   f'create?service_id={service_id}')
