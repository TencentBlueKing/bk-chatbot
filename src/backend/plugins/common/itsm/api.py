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

import time

from opsbot import CommandSession
from component import BKCloud


class GenericIT:
    def __init__(self, session: CommandSession, bk_env: str = 'v7'):
        self._session = session
        self.user_id = self._session.ctx['msg_sender_id']
        self._bk_service = BKCloud(bk_env).bk_service
        self._itsm = self._bk_service.itsm

    async def render_services(self):
        try:
            _, page = self._session.ctx['event_key'].split('|')
            page = int(page)
        except ValueError:
            return None

        services = await self._itsm.get_services()
        services = [{'id': str(var['id']), 'text': var['name']} for var in services]

        template_card = {
            'card_type': 'button_interaction',
            'source': {
                'desc': 'ITSM'
            },
            'main_title': {
                'title': '欢迎使用流程服务'
            },
            'task_id': str(int(time.time() * 100000)),
            'button_selection': {
                'question_key': 'bk_itsm_service_id',
                'title': '服务列表',
                'option_list': services[page:page+10]
            },
            'button_list': [
                {
                    "text": "提单",
                    "style": 1,
                    "key": "bk_itsm_select_service"
                },
                {
                    "text": "上页",
                    "style": 4,
                    "key": f"bk_itsm|{page - 10}"
                },
                {
                    "text": "下页",
                    "style": 4,
                    "key": f"bk_itsm|{page + 10}"
                }
            ]
        }
        return template_card

    async def render_service_detail(self):
        try:
            service_id = self._session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
        except KeyError:
            return None

        service = await self._itsm.get_service_detail(service_id=int(service_id))
        return {
            'card_type': 'text_notice',
            'source': {
                'desc': 'ITSM'
            },
            'main_title': {
                'title': f'已选择服务模版「{service["name"]}」点击填单'
            },
            'quote_area': {
                'quote_text': '\n'.join([field['name'] for field in service['fields']])
            },
            'task_id': str(int(time.time() * 100000)),
            'card_action': {
                'type': 1,
                'url': f'{self._bk_service.BK_ITSM_DOMAIN}#/ticket/create?service_id={service_id}'
            }
        }
