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

import hashlib
from collections import defaultdict
from typing import Dict

import aiohttp

from opsbot import CommandSession
from component import RedisClient


class DispatchMSG:
    def __init__(self, session: CommandSession):
        self._session = session
        self._redis_client = RedisClient(env="prod")

    async def handle_approve(self, callback: Dict):
        await self.call_backend(callback)
        return '已同意'

    async def handle_refuse(self, callback: Dict):
        await self.call_backend(callback)
        return '已拒绝'

    def handle_check(self):
        pass

    def is_exist(self, callback: str) -> bool:
        key = hashlib.md5(callback.encode('ascii')).hexdigest()
        data = self._redis_client.get(key)
        if not data:
            self._redis_client.set(key, self._session.ctx['msg_sender_id'], ex=60 * 60 * 60, nx=True)
            return False

        return True

    async def call_backend(self, callback: Dict):
        try:
            url = callback['url']
            method = callback['method'].upper()
        except (KeyError, AttributeError):
            return

        data = callback.get('params') or {}
        data.update({'username': self._session.ctx['msg_sender_id']})
        params = defaultdict(dict)
        if method == 'GET':
            params['params'] = data
        elif method == 'POST':
            params['json'] = data

        async with aiohttp.request(method, url, **params) as resp:
            return await resp.text()

    def process_msg(self) -> Dict[str, Dict]:
        try:
            payload = self._session.ctx['payload']
        except KeyError:
            return {}
        self.trans_user_id(payload)
        self.add_event(payload)
        return payload

    def trans_user_id(self, payload: Dict):
        receiver = payload.get('receiver')
        if not receiver:
            return

        if isinstance(receiver, dict) and receiver.get('type') == 'single':
            receiver.update({'id', self._session.bot.convert_to_name(receiver.get('id'))})

    @classmethod
    def add_event(cls, payload: Dict):
        pass
