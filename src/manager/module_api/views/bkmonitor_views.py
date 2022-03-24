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
from src.manager.handler.api.bk_monitor import BkMonitor
from src.manager.module_api.serializers import BkMonitorSerializer

BACKEND_USERNAME = os.getenv("PLUGIN_USER_NAME", "admin")


class BkMonitorViewSet(BaseViewSet):
    """
    蓝鲸监控
    """

    throttle_classes = (ChatBotThrottle,)
    http_method_names = ["post"]

    @login_exempt
    @csrf_exempt
    @check_permission()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @action(detail=False, methods=["POST"])
    def get_metric_data(self, request):
        """
        metric: cpu/memory/network/
        kwargs = {
            'biz_id': 883,
            'ip': 'x.x.x.x',
            'bk_cloud_id': 0,
            'start_timestamp': 1638374400000,
            'end_timestamp': 1638460799000,
        }
        """
        serializer = BkMonitorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query_params = serializer.validated_data
        metric_name = query_params.pop("metric")

        res = BkMonitor.get_ts_data(BACKEND_USERNAME, metric_name, **query_params)
        return Response(res)
