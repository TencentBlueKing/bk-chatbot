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

from blueapps.utils.logger import logger
from rest_framework.decorators import action
from rest_framework.response import Response

from common.control.throttle import ChatBotThrottle
from common.drf.generic import BaseViewSet
from common.http.request import get_request_user
from common.redis import RedisClient
from src.manager.handler.api.bk_cc import CC


class BizViewSet(BaseViewSet):
    """
    业务信息
    """

    throttle_classes = (ChatBotThrottle,)

    @action(detail=False, methods=["POST"])
    def describe_biz(self, request):
        """
        @api {get} api/v1/biz/describe_biz/ 获取当前用户有权限的业务信息
        @apiDescription 获取当前用户有权限的业务信息
        @apiName describe_biz
        @apiGroup Biz
        @apiSuccessExample {json} 返回:
        {
            "data": [
                {
                    "bk_biz_id": 1,
                    "default": 0,
                    "bk_biz_name": "业务1"
                }
            ],
            "code": 200,
            "message": "OK",
            "result": true,
            "request_id": "request_id"
        }
        """
        username = get_request_user(request)
        data = CC().search_business(
            username,
            {},
            fields=["bk_biz_id", "bk_biz_name"],
        )
        key = f"user_visited_{username}"
        record = RedisClient().get(key)
        if record and data:
            biz_id = record.get("biz_id", "-1")
            try:
                cursor = [
                    i
                    for i, __ in enumerate(
                        data,
                    )
                    if __["bk_biz_id"] == int(biz_id)
                ][0]
                data[0], data[cursor] = data[cursor], data[0]
            except IndexError:
                logger.error(f"查询redis中的业务ID为{biz_id}的业务数据失败")
        return Response(data)
