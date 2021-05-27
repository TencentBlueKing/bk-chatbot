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
from rest_framework.decorators import action
from rest_framework.response import Response

from common.generic import APIModelViewSet
from common.generic import ValidationMixin
from common.pagination import ResultsSetPagination
from module_intent.control.permission import IntentPermission
from module_intent.control.serializers import BotSerializer
from module_intent.control.throttle import IntentThrottle
from module_intent.models import Bot


class BotViewSet(APIModelViewSet, ValidationMixin):
    """
    机器人接入
    """

    queryset = Bot.objects.all()
    serializer_class = BotSerializer
    filter_fields = {
        "biz_id": ["exact"],
        "biz_name": ["exact"],
        "bot_id": ["exact"],
        "bot_name": ["exact"],
        "bot_type": ["exact"],
        "created_by": ["exact"],
        "is_deleted": ["exact"],
    }
    ordering_fields = [
        "biz_id",
        "biz_name",
        "bot_id",
        "created_by",
        "updated_at",
    ]
    ordering = "-updated_at"
    permission_classes = (IntentPermission,)
    throttle_classes = (IntentThrottle,)
    pagination_class = ResultsSetPagination

    @action(detail=False, methods=["POST"])
    def fetch_bot_count(self, request, *args, **kwargs):
        """
        获取机器人数
        @api {post} api/v1/bot/{biz_id}/fetch_bot_count/ 获取机器人数
        @apiDescription 获取机器人数
        @apiName fetch_bot_count
        @apiGroup Bot
        @apiRequestExample {json}:
        {
            "biz_id": xxx
        }
        @apiSuccessExample {json} 返回:
        {
            "result": true,
            "code": "200",
            "message": "success",
            "data": {
                "count": 2
            },
            "request_id": "xxxxxxxxxx"
        }
        """
        return Response(
            {
                "count": Bot.objects.filter(
                    biz_id=int(kwargs.get("biz_id")), is_deleted=False
                ).count()
            }
        )
