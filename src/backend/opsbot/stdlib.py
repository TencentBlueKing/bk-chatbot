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
import random
import hashlib
from base64 import urlsafe_b64encode, urlsafe_b64decode

from Crypto.Cipher import AES


def escape(s: str, *, escape_comma: bool = True) -> str:
    s = s.replace('&', '&amp;') \
        .replace('[', '&#91;') \
        .replace(']', '&#93;')
    if escape_comma:
        s = s.replace(',', '&#44;')
    return s


def unescape(s: str) -> str:
    return s.replace('&#44;', ',') \
        .replace('&#91;', '[') \
        .replace('&#93;', ']') \
        .replace('&amp;', '&')


def pad(text, blocksize=16):
    """
    PKCS#5 Padding
    """
    pad = blocksize - (len(text) % blocksize)
    return text + pad * chr(pad)


def unpad(text):
    """
    PKCS#5 Padding
    """
    pad = ord(text[-1])
    return text[:-pad]


def salt(length=8):
    """
    生成长度为length 的随机字符串
    """
    aplhabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join([random.choice(aplhabet) for _ in range(length)])


class Aes(object):
    def __init__(self, app_id='', app_key=''):
        self.key = hashlib.md5(f"{app_id}{app_key}".encode("utf-8")).hexdigest()

    def decrypt_dict(self, ciphertext, base64=True):
        return json.loads(self.decrypt(ciphertext, base64))

    def encrypt_dict(self, value, base64=True):
        return self.encrypt(json.dumps(value), base64)

    def decrypt(self, ciphertext, base64=True):
        """
        AES Decrypt
        """
        if base64:
            ciphertext = urlsafe_b64decode(str(ciphertext + '=' * (4 - len(ciphertext) % 4)))

        data = ciphertext
        key = self.key.encode('utf-8')
        key = hashlib.md5(key).digest()
        cipher = AES.new(key, AES.MODE_ECB)
        return unpad(cipher.decrypt(data).decode())

    def encrypt(self, plaintext, base64=True):
        """
        AES Encrypt
        """
        key = self.key.encode('utf-8')
        key = hashlib.md5(key).digest()
        cipher = AES.new(key, AES.MODE_ECB)
        plaintext = pad(plaintext).encode('utf-8')
        ciphertext = cipher.encrypt(plaintext)

        # 将密文base64加密
        if base64:
            ciphertext = urlsafe_b64encode(ciphertext).decode().rstrip('=')

        return ciphertext
