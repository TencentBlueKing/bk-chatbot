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

import traceback

from blueapps.utils.logger import logger
from django.conf import settings
from django.db.utils import IntegrityError
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    drf 异常处理
    """

    # debug模式打印错误信息
    if getattr(settings, "DEBUG"):
        traceback.print_exc()
    logger.error({"message": f"{traceback.format_exc()}"})
    logger.error({"message": f"exc:{exc}"})
    if isinstance(exc, IntegrityError):
        message = f"{exc.args[1]}" if len(exc.args) == 2 else f"{exc.args}"
    else:
        message = exc.args[0] if len(exc.args) == 1 else repr(exc)
    return Response(
        {"message": message},
        status=getattr(exc, "ERROR_CODE", 400),
    )
