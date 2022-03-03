# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import base64

from Crypto.Cipher import AES
from django.conf import settings


class BaseCrypt(object):
    _bk_crypt = False

    # KEY 和 IV 的长度需等于16
    ROOT_KEY = b"TencentBkApp-Key"
    ROOT_IV = b"TencentBkApp--Iv"

    def __init__(self, instance_key=settings.SECRET_KEY):
        self.INSTANCE_KEY = instance_key

    def encrypt(self, plaintext):
        """
        加密
        :param plaintext: 需要加密的内容
        :return:
        """
        decrypt_key = self.__parse_key()
        secret_txt = AES.new(decrypt_key, AES.MODE_CFB, self.ROOT_IV).encrypt(plaintext)
        return base64.b64encode(secret_txt).decode("utf-8")

    def decrypt(self, ciphertext):
        """
        解密
        :param ciphertext: 需要解密的内容
        :return:
        """
        decrypt_key = self.__parse_key()
        # 先解base64
        secret_txt = base64.b64decode(ciphertext)
        # 再解对称加密
        plain = AES.new(decrypt_key, AES.MODE_CFB, self.ROOT_IV).decrypt(secret_txt)
        return plain.decode(encoding="utf-8")

    def __parse_key(self):
        return self.INSTANCE_KEY[:24].encode()
