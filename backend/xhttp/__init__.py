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

import logging
from collections import defaultdict

from typing import Dict, Any, Optional, AnyStr, Callable, Union, List
from quart import Quart, request, abort, jsonify
from .api import HttpApi, UnifiedApi
from .bus import EventBus
from .exceptions import *
from .message import MessageSegment
from .decryption import Decryption
from .decryption.config import CORPID


def _deco_maker(post_type: str) -> Callable:
    def deco_deco(self, arg: Optional[Union[str, Callable]] = None, *events: str) -> Callable:
        def deco(func: Callable) -> Callable:
            if isinstance(arg, str):
                e = [post_type + '.' + e for e in [arg] + list(events)]
                self.on(*e)(func)
            else:
                self.on(post_type)(func)
            return func
        if isinstance(arg, Callable):
            return deco(arg)
        return deco
    return deco_deco


class XWorkHttp:
    def __init__(self,
                 api_root: Optional[str] = None,
                 access_token: Optional[str] = None,
                 secret: Optional[AnyStr] = None,
                 enable_http_post: bool = True,
                 message_class: type = None,
                 *args, **kwargs):
        self._access_token = access_token
        self._secret = secret
        self._bus = EventBus()
        self._server_app = Quart(__name__)

        self._server_app.route('/', methods=['GET'])(self._handle_url_verify)
        if enable_http_post:
            self._server_app.route('/', methods=['POST'])(self._handle_http_event)

        self._api = UnifiedApi(http_api=HttpApi(api_root, access_token))
        self._message_class = message_class

    def __getattr__(self, item) -> Callable:
        return self._api.__getattr__(item)

    @property
    def asgi(self) -> Quart:
        return self._server_app

    @property
    def server_app(self) -> Quart:
        return self._server_app

    @property
    def logger(self) -> logging.Logger:
        return self._server_app.logger

    def subscribe(self, event: str, func: Callable) -> None:
        self._bus.subscribe(event, func)

    def unsubscribe(self, event: str, func: Callable) -> None:
        self._bus.unsubscribe(event, func)

    def on(self, *events: str) -> Callable:
        def deco(func: Callable) -> Callable:
            for event in events:
                self.subscribe(event, func)
            return func

        return deco

    on_text = _deco_maker('text')
    on_event = _deco_maker('Event')
    on_emotion = _deco_maker('emotion')
    on_image = _deco_maker('image')
    on_file = _deco_maker('file')
    on_voice = _deco_maker('voice')
    on_mixed = _deco_maker('mixed')
    on_forward = _deco_maker('forward')

    async def _handle_url_verify(self):
        decryption = Decryption(request.args.get("msg_signature"), request.args.get("timestamp"),
                                request.args.get("nonce"), request.args.get("echostr"))
        return decryption.is_valid()

    async def _handle_http_event(self):
        """
        parse url, get path parameter
        data may in get_data
        :param self:
        :return: response
        """
        decryption = Decryption(request.args.get("msg_signature"), request.args.get("timestamp"),
                                request.args.get("nonce"), await request.get_data())
        payload = decryption.parse()
        if not isinstance(payload, dict):
            abort(400)

        response = await self._handle_event_payload(payload)
        return jsonify(response) if isinstance(response, dict) else ''

    async def _handle_event_payload(self, payload: Dict[str, Any]) -> Any:
        """
        todo define Event
        """
        post_type = payload.get("MsgType")
        detailed_type = payload.get("Event", "default")
        if not post_type or not detailed_type:
            return

        event = post_type + '.' + detailed_type
        context = payload.copy()
        if self._message_class and "Content" in context:
            context['message'] = self._message_class(context.get("Content"))
        results = list(filter(lambda r: r is not None, await self._bus.emit(event, context)))
        # return the first non-none result
        return results[0] if results else None

    async def _handle_event_payload_with_response(self, payload: Dict[str, Any]) -> None:
        response = await self._handle_event_payload(payload)
        if isinstance(response, dict):
            try:
                await self._api.call_action(
                    action='.handle_quick_operation_async',
                    context=payload, operation=response
                )
            except Error:
                pass

    def run(self, host=None, port=None, *args, **kwargs):
        self._server_app.run(host=host, port=port, *args, **kwargs)

    async def call_action(self, action: str, **params) -> Any:
        return await self._api.call_action(action=action, **params)

    async def send(self, context: Dict[str, Any],
                   message: Union[str, Dict[str, Any], List[Dict[str, Any]]],
                   **kwargs) -> Optional[Dict[str, Any]]:
        """
        Send text (default)
        """
        payload = defaultdict(dict)
        payload['touser'] = context['FromUserName']
        payload['agentid'] = context['AgentID']
        payload['text']['content'] = message
        payload['msgtype'] = "text"
        payload.update(kwargs)

        return await self.call_action('message/send', **payload)
