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
import uuid
from typing import Any, Optional, Dict, Union, List

from quart import request, abort, jsonify

from opsbot.log import logger
from opsbot.proxy import (
    Api as BaseApi, Proxy as BaseProxy, UnifiedApi, _deco_maker,
    ActionFailed, ApiNotAvailable, HttpFailed, NetworkError
)
from .message import Message
from .decryption import WXBizJsonMsgCrypt


class Proxy(BaseProxy):
    def __init__(self, api_root: Optional[str], api_config: Dict):
        super().__init__(message_class=Message,
                         api_class=UnifiedApi(http_api=HttpApi(api_root, api_config)))
        self._server_app.route('/callback', methods=['POST', 'GET'])(self._handle_http)

    on_text = _deco_maker('text')
    on_event = _deco_maker('event')

    @classmethod
    async def _handle_url_verify(cls, crypt: WXBizJsonMsgCrypt):
        """处理URL验证"""
        msg_signature = request.args.get("msg_signature")
        timestamp = request.args.get("timestamp")
        nonce = request.args.get("nonce")
        echostr = request.args.get("echostr")

        logger.info("验证 URL")
        ret, echostr = crypt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        if ret != 0:
            logger.error("URL 验证失败")
            abort(500)
        return echostr

    async def _handle_http(self):
        """处理HTTP请求"""
        token = self._api._api_config.get('TOKEN', '')
        encoding_aes_key = self._api._api_config.get('ENCODING_AES_KEY', '')
        receive_id = self._api._api_config.get('RECEIVE_ID', '')

        crypt = WXBizJsonMsgCrypt(token, encoding_aes_key, receive_id)

        # GET请求用于URL验证
        if request.method == 'GET':
            return await self._handle_url_verify(crypt)

        # POST请求用于接收消息
        msg_signature = request.args.get("msg_signature")
        timestamp = request.args.get("timestamp")
        nonce = request.args.get("nonce")

        post_data = await request.get_data()
        post_data = json.loads(post_data.decode("utf-8"))
        logger.info(f"请求消息回调 {post_data}, msg_signature={msg_signature}, timestamp={timestamp}, nonce={nonce}")

        ret, decrypt_post_json_data = crypt.DecryptMsg(post_data, msg_signature, timestamp, nonce)
        if ret != 0:
            logger.error("消息内容解密失败")
            abort(500)

        payload = json.loads(decrypt_post_json_data)
        logger.info(f"企微发送的消息\n=============\n{payload}")

        post_type = payload.get("msgtype")
        if not post_type:
            return jsonify({})

        event = f'{post_type}.default'
        context = payload.copy()

        if self._message_class and "text" in context:
            context['message'] = self._message_class(context.get("text", {}).get("content", ""))

        context['msg_type'] = post_type
        context['msg_from_type'] = 'single'
        context['msg_id'] = payload.get("msgid", "")
        context['msg_sender_id'] = payload.get("userid", "")
        context['msg_group_id'] = 'anonymous'
        context['create_time'] = payload.get("createtime", "")

        results = list(filter(lambda r: r is not None, await self._bus.emit(event, context)))

        # 返回流式消息
        return jsonify({
            "msgtype": "stream",
            "stream": {
                "id": f"stream_queue_{uuid.uuid4().hex}",
                "finish": True,
                "content": results[0] if results else "收到消息",
            }
        })

    async def call_action(self, action: str, **params) -> Any:
        return await self._api.call_action(action=action, json=params)

    def run(self, host=None, port=None, *args, **kwargs):
        self._server_app.run(host=host, port=port, *args, **kwargs)

    async def send(self, context: Dict[str, Any],
                   message: Union[str, Dict[str, Any], List[Dict[str, Any]]],
                   **kwargs):
        """发送消息"""
        payload = {
            "msgtype": "stream",
            "stream": {
                "id": f"stream_queue_{uuid.uuid4().hex}",
                "finish": True,
                "content": message if isinstance(message, str) else json.dumps(message),
            }
        }
        payload.update(kwargs)
        return payload


class HttpApi(BaseApi):
    def __init__(self, api_root: Optional[str], api_config: Dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_config = api_config
        self._api_root = api_root.rstrip('/') if api_root else None

    async def call_action(self, action: str, method='POST', **params) -> Optional[Dict[str, Any]]:
        """调用API"""
        if not self._is_available():
            raise ApiNotAvailable
        # 这里可以根据需要实现具体的API调用逻辑
        return {}

    def _is_available(self) -> bool:
        return True
