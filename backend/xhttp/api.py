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

import abc
import functools
import json
import sys

from typing import Callable, Dict, Any, Optional
import requests
import aiohttp

from .exceptions import *
from .decryption.config import CORPID, SECRET


class Api:
    """
    API interface.
    """

    def __getattr__(self, item: str) -> Callable:
        """
        Get a callable that sends the actual API request internally.
        """
        return functools.partial(self.call_action, item)

    @abc.abstractmethod
    async def call_action(self, action: str, **params) -> Optional[Dict[str, Any]]:
        """
        Send API request to call the specified action.
        """
        pass


def _handle_api_result(result: Optional[Dict[str, Any]]) -> Any:
    """
    Retrieve 'data' field from the API result object.
    Have change to adapt to xwork
    :param result: API result that received from HTTP API
    :return: the 'data' field in result object
    :raise ActionFailed: the 'status' field is 'failed'
    """
    if isinstance(result, dict):
        if result.get('errcode') != 0:
            raise ActionFailed(retcode=result.get('errcode'))
        return result


def _get_access_token(token_root) -> Any:
    try:
        response = requests.get(
            f"{token_root}/gettoken?corpid={CORPID}&corpsecret={SECRET}").json()
    except json.decoder.JSONDecodeError:
        return ""

    return response['access_token'] if response['errcode'] == 0 else ""


class HttpApi(Api):
    """
    Call APIs through HTTP.
    """

    def __init__(self, api_root: Optional[str], access_token: Optional[str], *args, **kwargs):
        """
        Dynamic get access_token
        """
        super().__init__(*args, **kwargs)
        self._api_root = api_root.rstrip('/') if api_root else None
        self._access_token = access_token

    async def call_action(self, action: str, **params) -> Any:
        if not self._is_available():
            raise ApiNotAvailable

        if self._access_token:
            url = f"{self._api_root}/{action}?access_token={self._access_token}"
        else:
            url = f"{self._api_root}/{action}?access_token={_get_access_token(self._api_root)}"

        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                async with session.post(url, data=json.dumps(params)) as resp:
                    if 200 <= resp.status < 300:
                        return _handle_api_result(json.loads(await resp.text()))
                    raise HttpFailed(resp.status)
        except aiohttp.InvalidURL:
            raise NetworkError('API root url invalid')
        except aiohttp.ClientError:
            raise NetworkError('HTTP request failed with client error')

    def _is_available(self) -> bool:
        return bool(self._api_root)


class _SequenceGenerator:
    _seq = 1

    @classmethod
    def next(cls) -> int:
        s = cls._seq
        cls._seq = (cls._seq + 1) % sys.maxsize
        return s


class UnifiedApi(Api):
    """
    Call APIs through different communication methods
    depending on availability.
    """

    def __init__(self, *args,
                 http_api: Api = None,
                 ws_reverse_api: Api = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._http_api = http_api
        self._ws_reverse_api = ws_reverse_api

    async def call_action(self, action: str, **params) -> Any:
        result = None
        succeeded = False

        if self._ws_reverse_api:
            # WebSocket is preferred
            try:
                result = await self._ws_reverse_api.call_action(action, **params)
                succeeded = True
            except ApiNotAvailable:
                pass

        if not succeeded and self._http_api:
            try:
                result = await self._http_api.call_action(action, **params)
                succeeded = True
            except ApiNotAvailable:
                pass

        if not succeeded:
            raise ApiNotAvailable

        return result
