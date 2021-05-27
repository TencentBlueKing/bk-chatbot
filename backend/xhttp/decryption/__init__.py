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

import xmltodict

from .config import CORPID, AES_KEY, TOKEN
from .wx_msg_crypt import WXBizMsgCrypt


class Decryption:
    """
    Decrypt
    Parse
    Classify: Event text
    """
    def __init__(self, msg_signature: str, timestamp: str, nonce: str, data: str):
        self.msg_signature = msg_signature
        self.timestamp = timestamp
        self.nonce = nonce
        self.data = data
        self.wxcpt = WXBizMsgCrypt(TOKEN, AES_KEY, CORPID)

    def _decrypt(self):
        r, context = self.wxcpt.decrypt_msg(self.data, self.msg_signature, self.timestamp, self.nonce)
        return context if r == 0 else None

    def is_valid(self):
        r, context = self.wxcpt.verify_url(self.msg_signature, self.timestamp, self.nonce, self.data)
        return context if r == 0 else None

    def parse(self):
        """
        :return:
        {
          "From": {
            "Type": "group",
            "Id": "ww3032085602",
            "Sender": "T08810012A",
            "DeviceType": "win"
          },
          "CreateTime": "1616658100",
          "MsgType": "text/Event/file/image/emotion",
          "MsgId": "CIGABBC0/fCCBhjXwIC8goCAAyCLBw==",
          "Content"/"Event"/"PicUrl"/"MediaId"/"FileName"
        }
        """
        context = self._decrypt()
        if context:
            return xmltodict.parse(context).get("xml", {})
        return None
