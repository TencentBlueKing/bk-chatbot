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
import sys
from django.conf import settings
from django.utils import translation

from adapter.utils import build_auth_args

# from adapter.utils.local import get_request
from blueapps.utils import get_request


def _clean_auth_info_uin(auth_info):
    if "uin" in auth_info:
        # 混合云uin去掉第一位
        if auth_info["uin"].startswith("o"):
            auth_info["uin"] = auth_info["uin"][1:]
    return auth_info


def update_bkdata_auth_info(params):
    """
    更新参数中的数据平台鉴权信息
    """
    if settings.FEATURE_TOGGLE.get("bkdata_token_auth", "off") == "on":
        # 如果使用 bkdata token 鉴权，需要设置鉴权方式，如果是用户鉴权，直接沿用原来的用户
        params["bkdata_authentication_method"] = params.get("bkdata_authentication_method") or "token"
        params["bkdata_data_token"] = settings.BKDATA_DATA_TOKEN
    else:
        # 如果是用户授权，设置为admin超级管理员
        params["bkdata_authentication_method"] = "user"
        params["bk_username"] = "admin"
        params["operator"] = "admin"
    return params


# 后台任务 & 测试任务调用 ESB 接口不需要用户权限控制
if (
    "celery" in sys.argv
    or "shell" in sys.argv
    or ("runserver" not in sys.argv and sys.argv and "manage.py" in sys.argv[0])
):

    def add_esb_info_before_request(params):
        params["bk_app_code"] = settings.APP_CODE
        params["bk_app_secret"] = settings.SECRET_KEY
        params.setdefault("bkdata_authentication_method", "user")

        if "bk_username" not in params:
            params["bk_username"] = "admin"

        if "operator" not in params:
            params["operator"] = params["bk_username"]
        return params

    def add_esb_info_before_request_for_bkdata(params):
        params = add_esb_info_before_request(params)
        params = update_bkdata_auth_info(params)
        return params


# 正常 WEB 请求所使用的函数
else:

    def add_esb_info_before_request(params):
        """
        通过 params 参数控制是否检查 request

        @param {Boolean} [params.no_request] 是否需要带上 request 标识
        """
        # 规范后的参数
        params["bk_app_code"] = settings.APP_CODE
        params["bk_app_secret"] = settings.SECRET_KEY
        params["appenv"] = settings.RUN_VER

        if "no_request" in params and params["no_request"]:
            params["bk_username"] = "admin"
            params["operator"] = "admin"
        else:
            req = get_request()
            auth_info = build_auth_args(req)
            params.update(auth_info)
            if not params.get("auth_info"):
                auth_info = _clean_auth_info_uin(auth_info)
                params["auth_info"] = json.dumps(auth_info)
            params.update({"blueking_language": translation.get_language()})

            bk_username = req.user.bk_username if hasattr(req.user, "bk_username") else req.user.username
            if "bk_username" not in params:
                params["bk_username"] = bk_username

            if "operator" not in params:
                params["operator"] = bk_username

        # 兼容旧接口
        params["uin"] = params["bk_username"]
        params["app_code"] = settings.APP_CODE
        params["app_secret"] = settings.SECRET_KEY
        params.setdefault("bkdata_authentication_method", "user")
        return params
