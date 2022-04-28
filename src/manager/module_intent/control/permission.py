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

from blueapps.utils.logger import logger
from rest_framework import permissions

from common.http.request import get_request_user
from common.redis import RedisClient
from src.manager.handler.api.bk_cc import CC


def record_user_visited(func):
    """
    记录用户访问
    """

    def _wrapped(*args, **kwargs):
        result = func(*args, **kwargs)

        try:
            username = args[1].user.username or args[1].COOKIES.get("bk_uid")
            biz_id = args[2].kwargs.get("biz_id", "-1")
        except IndexError:
            logger.error(f"[Decorator] args index error:{args}")
            return result

        key = f"user_visited_{username}"

        with RedisClient() as r:
            r.set(key, json.dumps({"biz_id": biz_id}))

        return result

    return _wrapped


class IntentPermission(permissions.BasePermission):
    """
    意图模块权限控制
    """

    @record_user_visited
    def has_permission(self, request, view):
        username = get_request_user(request)
        data = CC.search_business(username, {"bk_biz_id": int(view.kwargs.get("biz", "-1"))}, fields=["bk_biz_id"])
        if not data:
            logger.error(f"[Intent] user permission:{username}-{str(request.COOKIES)}")
            return False
        return True
