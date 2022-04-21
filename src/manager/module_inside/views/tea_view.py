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
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action

from common.control.throttle import ChatBotThrottle
from common.drf.validation import validation
from common.drf.view_set import BaseViewSet
from common.http.html import jsonify
from src.manager.handler.in_api.tea_api import TeaAPI
from src.manager.module_inside.proto.tea import (
    ReqGetProductSerializer,
    get_product_docs,
)


@method_decorator(name="get_product", decorator=get_product_docs)
class TeaViewSet(BaseViewSet):
    """
    Youti 相关操作
    """

    throttle_classes = (ChatBotThrottle,)

    @login_exempt
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @action(detail=False, methods=["GET"])
    @validation(ReqGetProductSerializer)
    def get_product(self, request):
        """
        @return:
        """
        payload = request.payload
        valid_projects = TeaAPI().get_valid_product(**payload)
        projects_info = list(
            map(
                lambda x: {
                    "name": x.get("name"),
                    "code": str(x.get("cc_id")),
                },
                valid_projects,
            )
        )
        return jsonify({"count": len(projects_info), "result": projects_info})
