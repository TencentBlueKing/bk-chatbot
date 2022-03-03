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
import uuid

from django.http import HttpResponse, JsonResponse


def error_response(error_msg: str) -> JsonResponse:
    """
    生成一个错误的json响应数据
    """
    return JsonResponse(
        {
            "code": 400,
            "result": False,
            "data": [],
            "message": error_msg,
            "request_id": str(uuid.uuid4()),
        }
    )


def jsonify(*args, **kwargs):
    """
    返回JSON
    """
    if "test" in kwargs:
        del kwargs["test"]

    status = kwargs.pop("code", 200)
    return HttpResponse(
        content=json.dumps(*args) if args else json.dumps(dict(**kwargs)),
        content_type="application/json",
        charset="utf-8",
        status=status,
    )
