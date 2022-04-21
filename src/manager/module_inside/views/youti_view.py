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

from blueapps.account.decorators import login_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.response import Response

from common.control.throttle import ChatBotThrottle
from common.drf.validation import validation
from common.drf.view_set import BaseViewSet
from common.http.html import jsonify
from common.http.request import init_views
from common.redis import RedisClient
from src.manager.handler.in_api.youti_api import MgaAPI
from src.manager.module_inside.handler.tea import get_product_users
from src.manager.module_inside.proto.youti import (
    ReqGetProductUsersSerializer,
    get_product_user_docs,
)


@method_decorator(name="get_product_users", decorator=get_product_user_docs)
class YoutiViewSet(BaseViewSet):
    """
    Youti 相关操作
    """

    throttle_classes = (ChatBotThrottle,)

    @login_exempt
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @action(detail=False, methods=["POST"])
    def get_cp(self, request):
        req_data, _ = init_views(request)
        return Response({"data": MgaAPI().get_cp(**req_data).get("data")})

    @action(detail=False, methods=["POST"])
    def send_msg(self, request):
        req_data, _ = init_views(request)
        return Response({"data": MgaAPI().send_msg(**req_data).get("data")})

    @action(detail=False, methods=["POST"])
    def send_custom_msg(self, request):
        req_data, _ = init_views(request)
        return Response({"data": MgaAPI().send_custom_msg(**req_data).get("data")})

    @action(detail=False, methods=["POST"])
    def get_bundle_id(self, request):
        req_data, _ = init_views(request)
        return Response({"data": MgaAPI().get_bundle_id(**req_data).get("data")})

    @action(detail=False, methods=["POST"])
    def get_user_info(self, request):
        req_data, _ = init_views(request)
        return Response({"data": MgaAPI().get_user_info(**req_data).get("data")})

    @action(detail=False, methods=["POST"])
    def get_user_info_by_phone(self, request):
        req_data, _ = init_views(request)
        return Response({"data": MgaAPI().get_user_info_by_phone(**req_data).get("data")})

    @action(detail=False, methods=["GET"])
    @validation(ReqGetProductUsersSerializer)
    def get_product_users(self, request):
        """
        获取业务信息
        @param request:
        @return:
        """
        payload = request.payload
        cc_id = payload.get("cc_id", None)
        # 如果查询全部的数据则从缓存中取数据
        if not cc_id:
            with RedisClient() as r:
                user_info_list = json.loads(r.get("YOUTI_USER_INFO"))
        else:
            product_users_list = get_product_users(cc_id)
            if len(product_users_list) == 0:
                return jsonify({"count": 0, "result": []})

            user_info_list = list(
                map(
                    lambda product_user: {
                        "username": f"qq_{product_user.get('user_qq')}",
                        "code": product_user.get("qq_unionid"),
                        "display_name": product_user.get("real_name"),
                        "departments": list(map(lambda x: str(x), product_user.get("product_list"))),
                    },
                    product_users_list,
                )
            )
        # 通过code_allow_null过滤数据
        code_allow_null = payload.get("code_allow_null", "1")
        new_user_info_list = (
            user_info_list if code_allow_null == "1" else list(filter(lambda x: x.get("code"), user_info_list))
        )
        return jsonify({"count": len(new_user_info_list), "result": new_user_info_list})
