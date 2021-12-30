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
from collections import defaultdict
from importlib import import_module
from typing import (
    Any, Optional, Dict, Union, List
)

import aiohttp
import requests
from quart import request, abort, jsonify, render_template
from jsonschema.exceptions import ValidationError

from .message import Message
from .decryption import Decryption
from opsbot.proxy import (
    Api as BaseApi, Proxy as BaseProxy, UnifiedApi, _deco_maker,
    ActionFailed, ApiNotAvailable, HttpFailed, NetworkError
)


class Proxy(BaseProxy):
    def __init__(self, api_root: Optional[str], api_config: Dict):
        super().__init__(message_class=Message,
                         api_class=UnifiedApi(http_api=HttpApi(api_root, api_config)))
        self._server_app.route('/api/<path:action>/', methods=['POST', 'GET'])(self._handle_api)

    on_text = _deco_maker('text')
    on_event = _deco_maker('event')

    @classmethod
    async def _validate_parameters(cls, module: Optional):
        if request.method == 'POST':
            try:
                payload = await request.json
            except TypeError:
                payload = await request.get_data()
        else:
            payload = request.args

        module.validate(payload)
        return payload

    async def _handle_api(self, action: str):
        try:
            module = import_module(f'plugins.sync.{action}')
        except ModuleNotFoundError:
            return jsonify({'msg': 'module failed', 'code': -1, 'result': False})

        try:
            payload = await self._validate_parameters(module)
        except ValidationError:
            return jsonify({'msg': 'params validate error', 'code': -1, 'result': False})

        result = await module.run(payload)
        return jsonify(result)

    @classmethod
    async def _handle_url_verify(cls):
        decryption = Decryption(request.args.get("msg_signature"), request.args.get("timestamp"),
                                request.args.get("nonce"), request.args.get("echostr"))
        return decryption.is_valid()

    async def _handle_http(self):
        decryption = Decryption(request.args.get("msg_signature"), request.args.get("timestamp"),
                                request.args.get("nonce"), await request.get_data())
        payload = decryption.parse()
        if not payload:
            return
        if not isinstance(payload, dict):
            abort(400)

        post_type = payload.get("MsgType")
        detailed_type = payload.get("Event", "default")
        if not post_type or not detailed_type:
            return

        event = post_type + '.' + detailed_type
        context = payload.copy()
        if self._message_class and "Content" in context:
            context['message'] = self._message_class(context.get("Content"))

        if "Event" in context:
            context['event'] = context.get("Event")
            context['event_key'] = context.get("EventKey")

        context['msg_type'] = context.get("MsgType")
        context['msg_from_type'] = 'single'
        context['msg_id'] = context.get("MsgId")
        context['msg_sender_id'] = context['msg_sender'] = context.get("FromUserName")
        context['msg_group_id'] = 'anonymous'
        context['create_time'] = context.get("CreateTime")

        results = list(filter(lambda r: r is not None, await self._bus.emit(event, context)))
        return jsonify(results[0]) if results else ''

    async def call_action(self, action: str, **params) -> Any:
        return await self._api.call_action(action=action, **params)

    def run(self, host=None, port=None, *args, **kwargs):
        self._server_app.run(host=host, port=port, *args, **kwargs)

    async def send(self, context: Dict[str, Any],
                   message: Union[str, Dict[str, Any], List[Dict[str, Any]]],
                   **kwargs):
        payload = defaultdict(dict)
        payload['touser'] = context['msg_sender_id']
        payload['agentid'] = context.get('AgentID', None) or context.get('AgentId')
        if message:
            payload['text']['content'] = message
        payload['msgtype'] = "text"
        payload.update(kwargs)

        return await self.call_action('message/send', **payload)


class HttpApi(BaseApi):
     def __init__(self, api_root: Optional[str], api_config: Dict, *args, **kwargs):
         super().__init__(*args, **kwargs)
         self._api_config = api_config
         self._api_root = api_root.rstrip('/') if api_root else None

     def _get_access_token(self, token_root) -> Any:
         try:
             response = requests.get(
                 f"{token_root}/gettoken?corpid={self._api_config['CORPID']}&corpsecret={self._api_config['SECRET']}"
             ).json()
         except TypeError:
             return ""

         return response['access_token'] if response['errcode'] == 0 else ""

     def _handle_api_result(self, result: Optional[Dict[str, Any]]) -> Any:
         if isinstance(result, dict):
             if result.get('errcode') != 0:
                 raise ActionFailed(retcode=result.get('errcode'))
             return result

     async def call_action(self, action: str, **params) -> Optional[Dict[str, Any]]:
         if not self._is_available():
             raise ApiNotAvailable

         url = f"{self._api_root}/{action}?access_token={self._get_access_token(self._api_root)}"
         print(url)
         try:
             async with aiohttp.request('POST', url, json=params) as resp:
                 if 200 <= resp.status < 300:
                     return self._handle_api_result(json.loads(await resp.text()))
                 raise HttpFailed(resp.status)
         except aiohttp.InvalidURL:
             raise NetworkError('API root url invalid')
         except aiohttp.ClientError:
             raise NetworkError('HTTP request failed with client error')

     def _is_available(self) -> bool:
         return bool(self._api_root)
