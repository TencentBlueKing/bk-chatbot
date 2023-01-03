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
from typing import Optional, Dict, Any, List

import aiohttp
from aiohttp.helpers import BasicAuth

from opsbot.log import logger
from component.exceptions import (
    ActionFailed, HttpFailed, NetworkError
)
from component.api import Api
from component.config import JIRA_USER_EMAIL, JIRA_TOKEN, JIRA_ROOT


class JiraApi(Api):
    def __init__(self, api_root: Optional[str], *args, **kwargs):
        super(JiraApi, self).__init__('jira', api_root, *args, **kwargs)
        self.auth = BasicAuth(JIRA_USER_EMAIL, JIRA_TOKEN)

    def _get_access_token(self) -> Optional[str]:
        return JIRA_TOKEN

    def _is_token_available(self) -> bool:
        return JIRA_TOKEN != ''

    def _handle_api_result(self, result: Optional[Dict[str, Any]]) -> Any:
        if 'errorMessages' not in result:
            return result
        logger.error(result)
        raise ActionFailed(retcode=result.get('code'), info=result)

    async def call_action(self, action: str = '', method: str = 'GET', **params) -> Any:
        url = f"{self._api_root}/{action}"
        if not self._is_token_available():
            return

        try:
            async with aiohttp.request(method, url,
                                       auth=self.auth,
                                       timeout=aiohttp.ClientTimeout(total=10),
                                       **params) as resp:
                if 200 <= resp.status < 300:
                    text = await resp.text()
                    if not text:
                        return
                    return self._handle_api_result(json.loads(text))
                logger.error(await resp.text())
                raise HttpFailed(resp.status)
        except aiohttp.InvalidURL:
            raise NetworkError('API root url invalid')
        except aiohttp.ClientError:
            raise NetworkError('HTTP request failed with client error')
        except aiohttp.ServerTimeoutError:
            raise NetworkError('Jira server timeout error')

    async def create(self, **params):
        return await self.call_action(method='POST', json=params)

    async def update(self, key, field, **params):
        return await self.call_action(action=f'{key}/{field}/', method='PUT', json=params)

    async def get(self, key: str, **params):
        return await self.call_action(action=key, params=params)


class User(JiraApi):
    def __init__(self):
        super(User, self).__init__(f'{JIRA_ROOT}user')

    async def search(self, query: str):
        return await self.call_action(action='search', params={'query': query})


class Issue(JiraApi):
    def __init__(self):
        super(Issue, self).__init__(f'{JIRA_ROOT}issue')


class IssueType(JiraApi):
    def __init__(self):
        super(IssueType, self).__init__(f'{JIRA_ROOT}issuetype')


class Tool(JiraApi):
    def __init__(self):
        super(Tool, self).__init__(f'{JIRA_ROOT}')

    async def search_by_obj(self, obj: str, key: str, **params):
        """
        :param obj: project
        :param key: PROJECT_NAME/PROJECT_ID
        :param params: maxResults=1&startAt=0&total=200
        :return: {issues:[]}
        """
        return await self.call_action(action=f'search?jql={obj}={key}', params=params)
