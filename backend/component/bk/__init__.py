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

from component.exceptions import *
from component.api import Api
from component.config import (
    BK_APP_ID, BK_APP_SECRET, BK_CC_ROOT,
    BK_JOB_ROOT, BK_SOPS_ROOT, BACKEND_ROOT
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
            if not result.get('result'):
                raise ActionFailed(retcode=result.get('code'))
            return result.get('data')

    async def call_action(self, action: str, method: str, **params) -> Any:
        if not self._is_available():
            raise ApiNotAvailable

        if not self._access_token:
            raise TokenNotAvailable

        url = f"{self._api_root}/{action}?{self._access_token}"
        params.get('json', {}).update(bk_app_code=BK_APP_ID, bk_app_secret=BK_APP_SECRET)
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


class CC:
    """
    CC api shortcut
    """

    def __init__(self):
        self.bk_cc_api = BKApi(BK_CC_ROOT)

    async def search_business(self, **params) -> Dict:
        """
        -params:
        bk_username
        """
        return await self.bk_cc_api.call_action('search_business/', 'POST', json=params)


class JOB:
    """
    JOB api shortcut
    """

    def __init__(self):
        self.bk_cc_api = BKApi(BK_JOB_ROOT)

    async def execute_job_plan(self, **params) -> Any:
        """
        -params:
        bk_biz_id
        job_plan_id
        global_var_list
        bk_supplier_account
        bk_username
        """
        return await self.bk_cc_api.call_action('execute_job_plan/', 'POST', json=params)


class SOPS:
    """
    sops api shortcut
    """

    def __init__(self):
        self.bk_cc_api = BKApi(BK_SOPS_ROOT)

    async def get_template_info(self, **params) -> Dict:
        """
        -params:
        template_id
        bk_biz_id
        """
        return await self.bk_cc_api.call_action(f'get_template_info/', 'GET', params=params)

    async def create_task(self, **params) -> Dict:
        """
        -params:
        template_id
        bk_biz_id
        -body
        constants
        exclude_task_nodes_id
        name
        bk_supplier_account
        bk_username
        """
        return await self.bk_cc_api.call_action(f'create_task/', 'POST', json=params)

    async def start_task(self, **params) -> Dict:
        """
        -params:
        task_id
        bk_biz_id
        -body
        bk_supplier_account
        bk_username
        """
        return await self.bk_cc_api.call_action(f'start_task/', 'POST', json=params)


class Backend:
    """
    Backend api shortcut
    """

    def __init__(self):
        self.bk_cc_api = BKApi(BACKEND_ROOT)

    async def describe(self, entity, **params) -> Dict:
        return await self.bk_cc_api.call_action(f'api/v1/exec/admin_describe_{entity}/',
                                                'POST', json={'data': params})
