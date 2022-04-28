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
from typing import Callable, Union

from django.http import JsonResponse

from common.http.html import error_response


def validation(valida):
    """
    验证器
    """

    def _validation(func):
        @wraps(func)
        def _wrapper(self, request, *args, **kwargs) -> Union[Callable, JsonResponse]:
            """
            用来验证请求数据是否存在
            """
            protocol = valida(data=request.payload)
            if protocol.is_valid():
                return func(self, request, *args, **kwargs)
            else:
                return error_response(protocol.errors)

        return _wrapper

    return _validation
