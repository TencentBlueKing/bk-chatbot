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

from blueapps.account.decorators import login_exempt
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.response import Response

from common.control.throttle import ChatBotThrottle
from common.generic import BaseViewSet
from common.http.request import init_views
from common.perm.permission import check_permission
from src.manager.handler.in_api.youti import Mga


class YoutiViewSet(BaseViewSet):
    """
    Youti 相关操作
    """

    throttle_classes = (ChatBotThrottle,)
    http_method_names = ["post"]

    @login_exempt
    @csrf_exempt
    @check_permission()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @action(detail=False, methods=["POST"])
    def get_cp(self, request):
        req_data, _ = init_views(request)
        return Response(Mga().get_cp(**req_data).get("data"))

    @action(detail=False, methods=["POST"])
    def send_msg(self, request):
        req_data, _ = init_views(request)
        return Response(Mga().send_msg(**req_data).get("data"))

    @action(detail=False, methods=["POST"])
    def send_custom_msg(self, request):
        req_data, _ = init_views(request)
        return Response(Mga().send_custom_msg(**req_data).get("data"))

    @action(detail=False, methods=["POST"])
    def get_bundle_id(self, request):
        req_data, _ = init_views(request)
        return Response(Mga().get_bundle_id(**req_data).get("data"))

    @action(detail=False, methods=["POST"])
    def get_user_info(self, request):
        req_data, _ = init_views(request)
        return Response(Mga().get_user_info(**req_data).get("data"))
