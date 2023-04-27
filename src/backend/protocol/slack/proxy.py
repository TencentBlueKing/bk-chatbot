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

from quart import request, jsonify, abort
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse

from opsbot.log import logger
from opsbot.proxy import (
    Api as BaseApi, Proxy as BaseProxy, UnifiedApi, _deco_maker,
    ActionFailed, ApiNotAvailable, HttpFailed, NetworkError
)
from .message import Message
from .decryption import Decryption


class Proxy(BaseProxy):
    def __init__(self, api_root: Optional[str], api_config: Dict):
        self.signing_secret = api_config.get('SIGNING_SECRET')
        super().__init__(message_class=Message,
                         api_class=UnifiedApi(http_api=HttpApi(api_config)))
        self._server_app.route('/open/callback/', methods=['POST'])(self._handle_http)
        self._server_app.register_error_handler(Exception, self._handle_bad_request)

    on_event_callback = _deco_maker('event_callback')
    on_interactive_message = _deco_maker('interactive_message')

    @classmethod
    async def _validate_parameters(cls):
        if request.method == 'POST':
            payload = await request.get_data()
        else:
            payload = request.args
        return payload

    @classmethod
    async def _handle_url_verify(cls):
        payload = await request.get_data()
        logger.debug(payload)
        return jsonify({'challenge': payload['challenge']})

    @classmethod
    async def _handle_bad_request(cls, e: Exception):
        logger.error(e)
        return jsonify(error='bad request', code=405)

    async def _handle_http(self):
        data = await self._validate_parameters()
        headers = dict(request.headers)
        decryption = Decryption(self.signing_secret, data, headers)
        if not decryption.is_valid():
            abort(400)

        payload = decryption.parse()
        post_type = payload.get('type')
        detailed_type = payload.get('event', {}).get('type', 'default')
        if not post_type or not detailed_type:
            abort(400)

        context = payload.copy()
        if post_type == 'event_callback':
            event = context['event']
            if detailed_type == 'message':
                if 'attachments' in event:
                    # user usually does not send button msg
                    abort(400)
                context['message'] = self._message_class(event.get("text"))
            context['msg_id'] = context.get("event_id")
            context['msg_group_id'] = event['channel']
            context['msg_sender_code'] = event['user']
            context['create_time'] = event.get("ts")
            if event['channel_type'] == 'im':
                context['msg_from_type'] = 'single'
            else:
                context['msg_from_type'] = 'group'
        elif post_type == 'interactive_message':
            context['msg_id'] = context.get("trigger_id")
            context['msg_group_id'] = context.get('channel', {}).get('id')
            context['msg_sender_code'] = context.get('user', {}).get('id')
            context['msg_from_type'] = 'single'
            context['create_time'] = context.get("message_ts")
            context['message'] = self._message_class(context.get("callback_id"))
        context['msg_sender_id'] = context['msg_sender_code']
        context['msg_type'] = post_type
        logger.debug(context)
        event = post_type + '.' + detailed_type
        results = list(filter(lambda r: r is not None, await self._bus.emit(event, context)))
        return jsonify(results[0]) if results else ''

    async def call_action(self, action, **params) -> Any:
        return await self._api.call_action(action=action, **params)

    def run(self, host=None, port=None, *args, **kwargs):
        self._server_app.run(host=host, port=port, *args, **kwargs)

    async def send(self, context: Dict[str, Any],
                   message: Union[str, Dict[str, Any], List[Dict[str, Any]]],
                   **kwargs):
        payload = defaultdict(dict)
        payload['channel'] = context['msg_group_id']
        if not message:
            payload['text'] = message
        action = kwargs.pop('action', 'chat_postMessage')
        payload.update(kwargs)
        return await self.call_action(action, **payload)


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

    def _handle_api_result(self, response: SlackResponse) -> Any:
        if not response.get('ok') or 'error' in response:
            logger.error(response)
            raise ActionFailed(retcode=response.get('error'))
        return {'result': response['ok']}

    async def call_action(self, action: str, **params) -> Optional[Dict[str, Any]]:
        """
        Send API request to call the specified action.
        - text: "Hello world!"
        """
        try:
            response = await getattr(self._client, action)(**params)
            return self._handle_api_result(response)
        except SlackApiError as e:
            logger.error(f'Slack Api error: {str(e)}')
            raise SlackApiError

    def _is_available(self) -> bool:
        return self._api_config.get('OAUTH_TOKEN')
