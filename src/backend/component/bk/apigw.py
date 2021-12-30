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

from typing import Dict, List

from .base import BKApi
from component.config import (
    BK_APP_ID, BK_APP_SECRET, BACKEND_ROOT, PLUGIN_ROOT,
    PLUGIN_TOKEN, BK_SUPER_USERNAME
)


class Backend:
    """
    Backend api shortcut
    """

    def __init__(self):
        self.bk_backend_api = BKApi(BACKEND_ROOT)

    async def describe(self, entity, **params) -> Dict:
        return await self.bk_backend_api.call_action(f'api/v1/exec/admin_describe_{entity}/',
                                                     'POST', json={'data': params})

    async def log(self, **params) -> Dict:
        return await self.bk_backend_api.call_action('api/v1/bot/log/create_log/', 'POST',
                                                     headers={'App-Id': BK_APP_ID, 'App-Token': BK_APP_SECRET},
                                                     json={'data': params})

    async def chat_bind(self, **params) -> Dict:
        return await self.bk_backend_api.call_action(f'api/v1/open_chat_bind/', 'POST', json=params)

    async def get_youti_user_info(self, **params) -> Dict:
        return await self.bk_backend_api.call_action(f'api/v1/youti/get_user_info', 'POST', json=params)

    async def get_opinion_type(self, **params) -> Dict:
        return await self.bk_backend_api.call_action(f'api/v1/ai/get_opinion_type/', 'POST', json=params)

    async def predict_intent(self, **params) -> Dict:
        return await self.bk_backend_api.call_action(f'api/v1/ai/predict_intent/', 'GET', params=params)

    async def set_timer(self, **params) -> Dict:
        return await self.bk_backend_api.call_action(f'api/v1/manage/timer/', 'POST', json=params)

    async def get_timer(self, **params) -> Dict:
        return await self.bk_backend_api.call_action(f'api/v1/manage/timer/', 'GET', params=params)

    async def delete_timer(self, timer_id: int) -> Dict:
        return await self.bk_backend_api.call_action(f'api/v1/manage/timer/{timer_id}/', 'DELETE')
