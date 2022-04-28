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
import time
import traceback

import jwt
import requests
from blueapps.utils.logger import logger


class BaseApi:
    def __init__(self, host, key, user, sub):
        self._host = host
        self._key = key
        self._user = user
        self._sub = sub
        self._headers = self._generate_headers()

    def _generate_headers(self):
        """
        用于jwt权限认证
        """
        payload = {
            "user": self._user,
            "sub": self._sub,
            "iat": int(time.time()),
        }
        encoded = str(jwt.encode(payload, self._key), encoding="utf-8")
        return {
            "Content-Type": "application/json",
            "AUTHORIZATION": f"Bearer {encoded}",
        }

    def _call(self, action: str, method: str, **kwargs):
        """
        @param action: 请求路由
        @param method: 请求方式:get/post/delete/put等
        @param kwargs: 请求参数设置json,data,headers等
        @return:
        """
        try:

            url = f"{self._host}{action}"
            kwargs["headers"] = self._headers

            # 记录请求数据
            logger.info(
                {
                    "message": json.dumps(
                        {
                            "url": url,
                            "method": method,
                            "params": kwargs,
                        }
                    )
                }
            )
            response = getattr(requests, method)(url, **kwargs)
            # 记录返回信息
            logger.info({"message": response.text})
            return response.json()
        except Exception:  # pylint: disable=broad-except
            logger.error({"message": traceback.format_exc()})
            return {"data": {}}
