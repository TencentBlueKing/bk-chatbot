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

from common.http.request import get_request_biz_id


def biz_id(func: Callable) -> Callable:
    """
    动态获取装饰器的内容
    @param func:
    @return:
    """

    @wraps(func)
    def _wrapper(self, request, *args, **kwargs) -> Callable:
        request.query_params._mutable = True
        cookie_biz_id = get_request_biz_id(request)
        if not cookie_biz_id:
            raise Exception("请求错误,请刷新重试")
        request.query_params["biz_id"] = cookie_biz_id
        return func(self, request, *args, **kwargs)

    return _wrapper
