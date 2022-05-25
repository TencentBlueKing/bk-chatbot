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

import json
import urllib
from typing import Any, Optional, Dict

import aiohttp

from opsbot.log import logger
from component.exceptions import *
from component.api import Api
from component.config import (
    BK_APP_ID, BK_APP_SECRET
)

_token = {}  # type: Dict[str, Any]


class BKApi(Api):
    """
    Call Component APIs through HTTP.
    """

    def __init__(self, api_root: Optional[str], *args, **kwargs):
        super().__init__('bk', api_root, *args, **kwargs)
        if not self._is_token_available():
            self._access_token = self._get_access_token()
            _token[BK_APP_ID] = self._access_token
        else:
            self._access_token = _token[BK_APP_ID]

    def _get_access_token(self) -> Any:
        """
        Native version don't need access_token
        by use add appid to the white paper
        Outer version can update the db and
        add the appid the field
        """
        return urllib.parse.urlencode({'bk_app_code': BK_APP_ID, 'bk_app_secret': BK_APP_SECRET})

    def _is_token_available(self) -> bool:
        if BK_APP_ID in _token:
            return True

        return False

    def _handle_api_result(self, result: Optional[Dict[str, Any]]) -> Any:
        if isinstance(result, dict):
            if result.get('result', False) or result.get('code', -1) == 0 or result.get('status', -1) == 0:
                return result.get('data')
            logger.error(result)
            raise ActionFailed(retcode=result.get('code'), info=result)

    async def call_action(self, action: str, method: str, **params) -> Any:
        if not self._is_available():
            raise ApiNotAvailable

        if not self._access_token:
            raise TokenNotAvailable

        url = f"{self._api_root}/{action}?{self._access_token}"

        try:
            async with aiohttp.request(method, url, **params) as resp:
                if 200 <= resp.status < 300:
                    return self._handle_api_result(json.loads(await resp.text()))
                raise HttpFailed(resp.status)
        except aiohttp.InvalidURL:
            raise NetworkError('API root url invalid')
        except aiohttp.ClientError:
            raise NetworkError('HTTP request failed with client error')

    def _is_available(self) -> bool:
        return bool(self._api_root and BK_APP_ID and BK_APP_SECRET)
