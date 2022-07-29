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


from functools import wraps
from typing import Callable

from django.conf import settings


class PermissionError(Exception):
    pass


def check_permission(*actions):
    """
    @param actions: actions为空全部不需要权限
    @return:
    """

    def perm_decorator(func: Callable) -> Callable:
        @wraps(func)
        def _wrapper(self, request, *args, **kwargs) -> Callable:

            method = request.method.lower()
            action_map = self.action_map.get(method, None)
            if actions and action_map not in actions:
                return func(self, request, *args, **kwargs)

            func.login_exempt = True

            # 获取变量
            app_id = settings.APP_CODE
            app_token = settings.SECRET_KEY
            if not app_id or not app_token:
                raise PermissionError("app_id or app_token not setting")

            bk_app_code = request.headers.get("App-Id", "")
            bk_app_secret = request.headers.get("App-Token", "")
            if bk_app_code == app_id and bk_app_secret == app_token:
                return func(self, request, *args, **kwargs)

            if (
                settings.DEBUG
                and request.payload.get("bk_app_code") == app_id
                and request.payload.get("bk_app_secret") == app_token
            ):
                return func(self, request, *args, **kwargs)
            raise PermissionError("bk_app_code or bk_app_secret is wrong")

        return _wrapper

    return perm_decorator


def login_exempt_with_perm(view_func):
    """
    登录豁免并鉴权
    @param view_func:
    @return:
    """

    def wrapped_view(self, request, *args, **kwargs):
        # 获取变量
        app_id = settings.APP_CODE
        app_token = settings.SECRET_KEY
        if not app_id or not app_token:
            raise PermissionError("app_id or app_token not setting")

        bk_app_code = request.headers.get("App-Id", "")
        bk_app_secret = request.headers.get("App-Token", "")
        if bk_app_code == app_id and bk_app_secret == app_token:
            return view_func(self, request, *args, **kwargs)

        if (
            settings.DEBUG
            and request.payload.get("bk_app_code") == app_id
            and request.payload.get("bk_app_secret") == app_token
        ):
            return view_func(self, request, *args, **kwargs)
        raise PermissionError("bk_app_code or bk_app_secret is wrong")

    wrapped_view.login_exempt = True
    return wraps(view_func)(wrapped_view)
