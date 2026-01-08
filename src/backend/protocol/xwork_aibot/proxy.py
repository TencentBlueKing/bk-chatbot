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
import os
import uuid
from typing import Any, Optional, Dict, Union, List

from quart import request, abort, jsonify
from quart import Response
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
                         api_class=UnifiedApi())
        self._server_app.route('/callback', methods=['POST', 'GET'])(self._handle_http)
        self.S_TOKEN = os.getenv("BKAPP_WXAIBOT_TOKEN")
        self.S_ENCODING_AES_KEY = os.getenv("BKAPP_WXAIBOT_ENCODING_AES_KEY")

    async def _handle_url_verify(self, request):
        """处理URL验证"""
        crypt = WXBizJsonMsgCrypt(self.S_TOKEN, self.S_ENCODING_AES_KEY, "")
        msg_signature = request.args.get("msg_signature")
        timestamp = request.args.get("timestamp")
        nonce = request.args.get("nonce")
        echostr = request.args.get("echostr")

        logger.info("验证 URL")
        ret, echostr = crypt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        logger.info(echostr)
        if ret != 0:
            logger.error("URL 验证失败")
            return jsonify({"error": "验证失败"}), 500
        return echostr

    async def _handle_http(self):
        """处理HTTP请求"""
        if request.method == 'GET':
            return await self._handle_url_verify(request)

        else:
            crypt = WXBizJsonMsgCrypt(self.S_TOKEN, self.S_ENCODING_AES_KEY, "")
            msg_signature = request.args.get("msg_signature")
            timestamp = request.args.get("timestamp")
            nonce = request.args.get("nonce")
            body = await request.get_data()
            post_data = json.loads(body.decode("utf-8"))
            logger.info(
                f"请求消息回调 {post_data}, msg_signature={msg_signature}, timestamp={timestamp}, nonce={nonce}")
            ret, decrypt_post_json_data = crypt.DecryptMsg(post_data, msg_signature, timestamp, nonce)
            if ret != 0:
                logger.error("消息内容解密失败")
                return jsonify({"error": "解密失败"}, status=500)
            post_json = json.loads(decrypt_post_json_data)
            logger.info(f"企微发送的消息\n=============\n{post_json}")
            return_msg = {
                "msgtype": "stream",
                "stream": {
                    "id": f"stream_queue_{uuid.uuid4().hex}",
                    "finish": True,
                    "content": post_json['text']['content'],
                }
            }
            ret, wxbot_encrypt_msg = crypt.EncryptMsg(json.dumps(return_msg, ensure_ascii=False), nonce, timestamp)
            logger.info(f"返回的消息\n=============\n{return_msg}")
            return Response(response=wxbot_encrypt_msg, content_type="text/plain")

    def run(self, host=None, port=None, *args, **kwargs):
        self._server_app.run(host=host, port=port, *args, **kwargs)
