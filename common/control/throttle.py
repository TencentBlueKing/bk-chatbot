# -*- coding: utf-8 -*-

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

from rest_framework.settings import api_settings
from rest_framework.throttling import BaseThrottle

from module_api.iaas.redis_client import RedisClient

RECORD = {"127.0.0.1": [1576141582]}


class ChatBotThrottle(BaseThrottle):
    ctime = time.time

    def __init__(self, num=20, times=1):
        # 允许1秒20次
        self.num_request = num
        self.times_request = times
        self.redis_client = RedisClient()

    def get_ident(self, request):
        """
        根据用户IP和代理IP，当做请求者的唯一IP
        Identify the machine making the request by parsing HTTP_X_FORWARDED_FOR
        if present and number of proxies is > 0. If not use all of
        HTTP_X_FORWARDED_FOR if it is available, if not use REMOTE_ADDR.
        """
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        remote_addr = request.META.get("REMOTE_ADDR")
        num_proxies = api_settings.NUM_PROXIES

        if num_proxies is not None:
            if num_proxies == 0 or xff is None:
                return remote_addr
            addrs = xff.split(",")
            client_addr = addrs[-min(num_proxies, len(addrs))]
            return client_addr.strip()

        return "".join(xff.split()) if xff else remote_addr

    def allow_request(self, request, view):
        """
        是否仍然在允许范围内
        Return `True` if the request should be allowed, `False` otherwise.
        :param request:
        :param view:
        :return: True，表示可以通过；False表示已超过限制，不允许访问
        """
        now = self.ctime()
        ident = self.get_ident(request)
        tms = self.redis_client.hash_get(
            f"{view.basename}_{view.action}",
            ident,
        )
        if not tms:
            self.redis_client.hash_set(
                f"{view.basename}_{view.action}",
                ident,
                json.dumps(
                    [
                        now,
                    ],
                ),
            )
            return True
        history = self.redis_client.hash_get(
            f"{view.basename}_{view.action}",
            ident,
        )
        history = json.loads(history)
        while history and history[-1] <= now - self.times_request:
            history.pop()
        if len(history) < self.num_request:
            history.insert(0, now)
            self.redis_client.hash_set(
                f"{view.basename}_{view.action}",
                ident,
                json.dumps(history),
            )
            return True

        return False
