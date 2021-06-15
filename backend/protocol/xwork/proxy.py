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

from collections import defaultdict
from typing import (
    Any, Optional, Dict, Union, List
)

from quart import request, abort, jsonify

from ..in_xwork.message import Message
from ..in_xwork.decryption import Decryption
from ..in_xwork.proxy import HttpApi
from opsbot.proxy import (
    Proxy as BaseProxy, UnifiedApi, _deco_maker,
)


class Proxy(BaseProxy):
    def __init__(self, api_root: Optional[str], api_config: Dict):
        super().__init__(message_class=Message,
                         api_class=UnifiedApi(http_api=HttpApi(api_root, api_config)))

    on_text = _deco_maker('text')
    on_event = _deco_maker('Event')

    @classmethod
    async def _handle_url_verify(cls):
        decryption = Decryption(request.args.get("msg_signature"), request.args.get("timestamp"),
                                request.args.get("nonce"), request.args.get("echostr"))
        return decryption.is_valid()

    async def _handle_http(self):
        decryption = Decryption(request.args.get("msg_signature"), request.args.get("timestamp"),
                                request.args.get("nonce"), await request.get_data())
        payload = decryption.parse()
        if not isinstance(payload, dict):
            abort(400)

        post_type = payload.get("MsgType")
        detailed_type = payload.get("Event", "default")
        if not post_type or not detailed_type:
            return

        event = post_type + '.' + detailed_type
        context = payload.copy()
        if self._message_class and "Content" in context:
            context['message'] = self._message_class(context.get("Msg", {}).get("Content"))

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
        payload['agentid'] = context['AgentID']
        payload['text']['content'] = message
        payload['msgtype'] = "text"
        payload.update(kwargs)

        return await self.call_action('message/send', **payload)

