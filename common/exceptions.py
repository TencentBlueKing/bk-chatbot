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

from django.utils.encoding import force_text
from django.utils.translation import ugettext as _


class ErrorCode:
    SYS_PLAT_CODE = "42"
    SYS_WEB_CODE = "00"
    SYS_BIZ_ACCESS = "01"
    SYS_MODULE_BIZ = "02"
    SYS_DATA_SOURCE = "03"
    SYS_CHART_CODE = "04"
    SYS_PLUGIN_CODE = "05"
    SYS_COMMON_CODE = "06"
    SYS_API_CODE = "07"
    SYS_BIZ = "08"
    SYS_PERMISSION = "09"
    SYS_REPORT = "10"
    SYS_APIGW = "11"
    SYS_NOTICE = "12"
    SYS_STATEMENT = "13"
    SYS_SCENE_MODEL = "14"


class BaseException(Exception):
    MODULE_CODE = ErrorCode.SYS_WEB_CODE
    ERROR_CODE = "500"
    MESSAGE = _("系统异常")

    def __init__(self, *args, **kwargs):
        """
        @param {String} code 自动设置异常状态码
        """
        super().__init__(*args)
        self.code = ErrorCode.SYS_PLAT_CODE + self.MODULE_CODE + self.ERROR_CODE
        self.errors = kwargs["errors"] if kwargs.get("errors") else None

        # 直接使用其它系统的错误编码
        if kwargs.get("code"):
            self.code = kwargs["code"]

        # 位置参数0是异常MESSAGE
        self.message = (
            force_text(self.MESSAGE)
            if len(args) == 0
            else force_text(
                f"{self.MESSAGE}: {args[0]}",
            )
        )

        # 位置参数1是异常后需返回的数据
        self.data = None if len(args) < 2 else args[1]

    def __str__(self):
        return f"[{self.code}] {self.message}"


class ValidationError(BaseException):
    MESSAGE = _("参数验证失败")
    ERROR_CODE = "001"


class RouteDisabledError(BaseException):
    MESSAGE = _("非法路由访问")
    ERROR_CODE = "400"
