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
import os

from blueapps.account.decorators import login_exempt
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.response import Response

from common.control.throttle import ChatBotThrottle
from common.generic import BaseViewSet
from common.perm.permission import check_permission
from src.manager.handler.api.bk_cc import CC
from src.manager.module_api.serializers import BkHostSerializer

BACKEND_USERNAME = os.getenv("PLUGIN_USER_NAME", "admin")


class CmdbViewSet(BaseViewSet):
    """
    配置平台
    """

    throttle_classes = (ChatBotThrottle,)
    http_method_names = ["post"]

    @login_exempt
    @csrf_exempt
    @check_permission()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @action(detail=False, methods=["POST"])
    def get_biz_host(self, request):
        """获取业务主机列表"""

        serializer = BkHostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query_params = serializer.validated_data

        data = CC().list_biz_hosts(BACKEND_USERNAME, query_params)

        return Response(data)

    @action(methods=["POST"], detail=False)
    def get_topo_tree_list(self, request, *args, **kwargs):
        """获取主机拓扑列表"""

        serializer = BkHostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query_params = serializer.validated_data

        biz_sets = CC().search_biz_inst_topo(BACKEND_USERNAME, query_params)

        def pop_noused(obj):
            for key in ["bk_inst_id", "bk_inst_name", "bk_obj_id", "bk_obj_name", "default"]:
                obj.pop(key, None)

        # 调整为前端需要的结构，且id设置为字符串
        for biz_set in biz_sets:
            biz_set.update({"id": str(biz_set["bk_inst_id"]), "name": biz_set["bk_inst_name"]})
            pop_noused(biz_set)
            biz_set.update(children=biz_set.pop("child"))
            for biz_module in biz_set["children"]:
                biz_module.update({"id": str(biz_module["bk_inst_id"]), "name": biz_module["bk_inst_name"]})
                pop_noused(biz_module)
                biz_module.pop("child")

        return Response(biz_sets)
