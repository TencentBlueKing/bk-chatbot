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
from itertools import chain
from typing import Callable

from common.http.request import get_request_biz_id, get_request_user
from src.manager.handler.api.bk_cc import CC


def check_biz_ops(func: Callable) -> Callable:
    """
    判断是不是业务负责人
    @return:
    """

    @wraps(func)
    def _wrapper(self, request, *args, **kwargs):
        """
        权限控制逻辑
        @param self:
        @param request:
        @param args:
        @param kwargs:
        @return:
        """

        biz_id = get_request_biz_id(request)
        username = get_request_user(request)
        if not biz_id or not username:
            raise ValueError(f"查询出的业务ID「{biz_id}」或者用户「{username}」为空")

        # 通过biz_id查询业务
        data = CC.search_business(
            **{
                "bk_username": username,
                "fields": ["bk_biz_id", "bk_biz_name", "bk_biz_maintainer", "bk_oper_plan"],
                "biz_ids": [int(biz_id)],
            }
        )
        # 查询数量为0则进行异常处理
        if len(data) == 0:
            raise ValueError(f"通过业务ID{biz_id}查询的业务数量为0")

        # 判断用户是否具有业务权限
        user_list = set(
            chain.from_iterable(
                [x.get("bk_biz_maintainer").split(",") + x.get("bk_oper_plan").split(",") for x in data]
            )
        )

        if username not in user_list:
            raise ValueError(f"{username}不属于业务PM或者业务运维")
        return func(self, request, *args, **kwargs)

    return _wrapper
