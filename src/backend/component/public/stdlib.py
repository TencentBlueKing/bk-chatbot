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

import re
import base64, hmac, json
from importlib import import_module
from typing import Dict, ByteString

from hashlib import sha1
from Crypto.Cipher import AES

from component.config import AES_KEY, AES_IV


def regex_parse_entity(regular, msg):
    regex = re.compile(regular)
    m = regex.search(msg)
    try:
        return m.group()
    except AttributeError:
        return None


def generate_hmac_token(key: ByteString, data: Dict, mod=sha1) -> str:
    return base64.b64encode(hmac.new(key, json.dumps(data).encode("utf-8"), digestmod=mod).digest())


class AesED(object):
    def __init__(self, key=AES_KEY, iv=AES_IV, mode=AES.MODE_CBC):
        self.key = key
        self.iv = iv
        self.mode = mode
        self.BS = len(key)
        self._pad = lambda s: s + (self.BS - len(s) % self.BS) * chr(self.BS - len(s) % self.BS)
        self._unpad = lambda s: s[0:-ord(s[-1:])]

    def encrypt(self, text):
        crypto = AES.new(self.key.encode("utf8"), self.mode, self.iv.encode("utf8"))
        cipher_text = crypto.encrypt(bytes(self._pad(text), encoding="utf8"))
        return base64.b64encode(cipher_text)

    def decrypt(self, text):
        decode = base64.b64decode(text)
        crypto = AES.new(self.key.encode("utf8"), self.mode, self.iv.encode("utf8"))
        plain_text = crypto.decrypt(decode)
        return self._unpad(plain_text)


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError('Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
        ) from err


class Response:
    def __init__(self, result=True, code=0, msg='', data={}):
        self.result = result
        self.code = code
        self.data = data
        self.msg = msg
