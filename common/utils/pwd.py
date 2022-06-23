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
import string
from base64 import b64decode, b64encode

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def gen_pwd(n: int) -> str:
    """
    生成密码
    """
    # sample从序列中选择n个随机独立的元素，返回列表
    num = random.sample(string.digits, 1)  # 随机取1位数字
    lower = random.sample(string.ascii_uppercase, 1)  # 随机取1位小写字母
    upper = random.sample(string.ascii_lowercase, 1)  # 随机取1位大写字母
    special = random.sample(string.punctuation, 1)  # 随机取1位大写字母特殊字符
    other = random.sample(string.ascii_letters + string.digits + string.punctuation, n)  # 随机取4位
    # 生成字符串
    # print(num, lower, upper, special, other)
    pwd_list = num + lower + upper + special + other
    # shuffle将一个序列中的元素随机打乱，打乱字符串
    random.shuffle(pwd_list)
    return "".join(pwd_list)


class AESClassicCipher:
    def __init__(self, key: str):
        self.bs = AES.block_size
        self.key = key.encode("utf-8")
        self.mode = AES.MODE_CBC

    def encrypt(self, data: str):

        """
        加密
        :param data:
        :return:
        """
        cipher = AES.new(self.key, self.mode)
        ct_bytes = cipher.encrypt(pad(data.encode("utf-8"), self.bs))
        iv = b64encode(cipher.iv).decode("utf-8")
        ct = b64encode(ct_bytes).decode("utf-8")
        encrypt_dict = json.dumps({"iv": iv, "ciphertext": ct})
        encrypt_str = b64encode(encrypt_dict.encode("utf-8")).decode("utf-8")
        return encrypt_str

    def decrypt(self, str_input):
        """
        解密
        :param str_input:
        :return:
        """
        json_input = b64decode(str_input)
        b64 = json.loads(json_input)
        iv = b64decode(b64["iv"])
        ct = b64decode(b64["ciphertext"])
        cipher = AES.new(self.key, self.mode, iv)
        plaintext = unpad(cipher.decrypt(ct), self.bs)
        return plaintext.decode("utf-8")
