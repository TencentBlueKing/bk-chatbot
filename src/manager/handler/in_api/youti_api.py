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

from common.utils.os import get_env_or_raise

from .base import BaseApi


class MgaAPI(BaseApi):
    def __init__(self, **kwargs):
        """
        使用默认配置
        """
        host = kwargs.get("host", get_env_or_raise("MGA_URL"))
        key = kwargs.get("key", get_env_or_raise("TEA_API_KEY"))
        user = kwargs.get("user", get_env_or_raise("TEA_OPERATOR"))
        sub = kwargs.get("sub", get_env_or_raise("TEA_API_ID"))
        super().__init__(host, key, user, sub)

    def get_cp(self, **params):
        """
        获取业务信息
        @param params:
        @return:
        """
        return self._call("web/api/product/cp-msg/get-cp/", "get", params=params)

    def send_msg(self, **params):
        """
        发送消息
        @param params:
        @return:
        """
        return self._call("web/api/product/cp-msg/sendmsg/", "get", params=params)

    def send_custom_msg(self, **params):
        """
        @param params:
        @return:
        """
        return self._call("web/api/product/cp-msg/send-custom-msg", "post", data=json.dumps(params))

    def get_bundle_id(self, **params):
        """
        @param params:
        @return:
        """
        return self._call("web/api/ops/info/get-bundle-id/", "get", params=params)

    def get_user_info(self, **params):
        """
        @param params:
        @return:
        """
        return self._call("api/ops/info/get-user-info/", "get", params=params)

    def get_user_info_by_phone(self, **params):
        """
        @param params:
        @return:
        """
        return self._call("api/ops/info/get-user-info-by-phone/", "get", params=params)
