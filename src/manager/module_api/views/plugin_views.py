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

from common.control.throttle import ChatBotThrottle
from common.drf.generic import BaseViewSet
from common.redis import RedisClient
from src.manager.handler.in_api.plugin import Service


class PluginViewSet(BaseViewSet):
    throttle_classes = (ChatBotThrottle,)
    http_method_names = ["post"]

    @action(detail=False, methods=["POST"])
    def call(self, request):
        """
        调用服务
        @param request:
        @return:
        """

        return Response(Service().call_service(**request.payload))

    @action(detail=False, methods=["POST"])
    def get_h5_config(self, request):
        return Response(RedisClient().get(request.payload.get("secret", "")))
