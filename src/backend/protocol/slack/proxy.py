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

from typing import (
    Any, Optional, Dict, Union, List
)
from collections import defaultdict
from ssl import SSLContext

from quart import request, jsonify
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

from opsbot.log import logger
from opsbot.proxy import (
    Api as BaseApi, Proxy as BaseProxy, UnifiedApi, _deco_maker,
    ActionFailed, ApiNotAvailable, HttpFailed, NetworkError
)
from .message import Message


class Proxy(BaseProxy):
    def __init__(self, api_root: Optional[str], api_config: Dict):
        super().__init__(message_class=Message,
                         api_class=UnifiedApi(http_api=HttpApi(api_config)))
        self._server_app.route('/open/callback/', methods=['POST'])(self._handle_http)
        self._server_app.register_error_handler(Exception, self._handle_bad_request)

    on_text = _deco_maker('text')

    @classmethod
    async def _handle_url_verify(cls):
        payload = await request.get_data()
        logger.info(payload)
        return jsonify({'challenge': payload['challenge']})

    @classmethod
    async def _handle_bad_request(cls, e: Exception):
        return jsonify(error='bad request', code=405)

    async def _handle_http(self):
        logger.debug(dict(request.headers))
        logger.debug(f'remote_addr: {request.remote_addr}')
        return await self._handle_url_verify()

    async def call_action(self, channel: str, **params) -> Any:
        return await self._api.call_action(channel, json=params)

    def run(self, host=None, port=None, *args, **kwargs):
        self._server_app.run(host=host, port=port, *args, **kwargs)

    async def send(self, context: Dict[str, Any],
                   message: Union[str, Dict[str, Any], List[Dict[str, Any]]],
                   **kwargs):
        payload = defaultdict(dict)
        channel = context['event']['channel']
        if not message:
            payload['text'] = message
        payload.update(kwargs)
        return await self.call_action(channel, **payload)


class HttpApi(BaseApi):
    def __init__(self, api_config: Dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_config = api_config
        if not self._is_available():
            raise ApiNotAvailable
        self._client = AsyncWebClient(token=self._get_access_token(),
                                      ssl=SSLContext())

    def _get_access_token(self) -> Any:
        return self._api_config['OAUTH_TOKEN']

    def _handle_api_result(self, result: Optional[Dict[str, Any]]) -> Any:
        if isinstance(result, dict):
            if not result.get('ok') or 'error' in result:
                logger.error(result)
                raise ActionFailed(retcode=result.get('error'))
            return result

    async def call_action(self, channel: str, **params) -> Optional[Dict[str, Any]]:
        """
        Send API request to call the specified action.
        - text: "Hello world!"
        """
        try:
            response = await self._client.chat_postMessage(channel=channel, **params)
            return self._handle_json_result(response)
        except SlackApiError as e:
            logger.error(f'Slack Api error: {str(e)}')
            raise SlackApiError

    def _is_available(self) -> bool:
        return self._api_config.get('OAUTH_TOKEN')
