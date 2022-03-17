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
import time

import jwt
import requests


class Mga:
    def __init__(self):
        self._host = os.getenv("MGA_URL")
        self._headers = self._generate_headers()

    @classmethod
    def _generate_headers(cls):
        payload = {
            "user": os.getenv("TEA_OPERATOR"),
            "sub": os.getenv("TEA_API_ID"),
            "iat": int(time.time()),
        }
        key = os.getenv("TEA_API_KEY", "bkchat")
        encoded = str(jwt.encode(payload, key), encoding="utf-8")
        return {
            "Content-Type": "application/json",
            "AUTHORIZATION": f"Bearer {encoded}",
        }

    def _call(self, action: str, method: str, **params):
        try:
            url = f"{self._host}{action}"
            params["headers"] = self._headers
            response = getattr(requests, method)(url, **params)
            return response.json()
        except Exception:  # pylint: disable=broad-except
            return {"data": {}}

    def get_cp(self, **params):
        return self._call("web/api/product/cp-msg/get-cp/", "get", params=params)

    def send_msg(self, **params):
        return self._call("web/api/product/cp-msg/sendmsg/", "get", params=params)

    def send_custom_msg(self, **params):
        return self._call("web/api/product/cp-msg/send-custom-msg", "post", data=json.dumps(params))

    def get_bundle_id(self, **params):
        return self._call("web/api/ops/info/get-bundle-id/", "get", params=params)

    def get_user_info(self, **params):
        return self._call("api/ops/info/get-user-info/", "get", params=params)
