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
import traceback

from blueapps.utils.logger import logger
from django.conf import settings

from common.http.html import error_response
from common.utils.local import local

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x


class CommonMiddleware(MiddlewareMixin):
    """
    通用中间件
    """

    def process_request(self, request):
        """
        入中间件用来处理请求数据
        """
        try:
            charset = request.encoding if request.encoding else "utf-8"
            if request.method != "GET" and "application/json" in request.content_type:
                payload = json.loads(str(request.body, encoding=charset))
            else:

                if request.method in ("GET", "POST"):
                    payload = getattr(request, request.method).dict()
                else:
                    request_body = request.body.decode(charset)
                    payload = {} if request_body == "" else json.loads(request_body)
        except Exception as ex:  # pylint: disable=broad-except
            traceback.print_exc()
            error_msg = f"parameter parsing error: {ex}"
            logger.error(error_msg)
            return error_response(error_msg)

        # 请求信息记录
        logger.info(
            {
                "message": json.dumps(
                    {
                        "url": request.get_full_path(),
                        "data": payload,
                    }
                )
            }
        )
        request.payload = payload
        return

    @staticmethod
    def process_exception(request, error: Exception):
        """
        用来处理异常
        """

        # debug模式打印错误信息
        if getattr(settings, "DEBUG"):
            traceback.print_exc()
        # 记录错误日志
        logger.error(json.dumps({"message": traceback.format_exc()}))
        return error_response(str(error))


class RequestProvider:
    """
    request_id中间件
    调用链使用
    """

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        local.request = request
        request.request_id = local.get_http_request_id()

        response = self.get_response(request)
        response["X-Request-Id"] = request.request_id

        local.release()

        return response

    # Compatibility methods for Django <1.10
    def process_request(self, request):
        local.request = request
        request.request_id = local.get_http_request_id()

    def process_response(self, request, response):
        response["X-Request-Id"] = request.request_id
        local.release()
        return response
