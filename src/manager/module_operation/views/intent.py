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
import datetime
from django.db.models import Count
from django.db.models.functions import Trunc
from common.drf.view_set import BaseViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from common.http.request import get_request_biz_id
from src.manager.module_intent.models import ExecutionLog


class IntentViewSet(BaseViewSet):
    schema = None

    @action(detail=False, methods=["GET"])
    def exec_info(self, request, *args, **kwargs):
        biz_id = get_request_biz_id(request)
        query_params = request.query_params
        start_time = datetime.datetime.strptime(query_params.get("start_time"), "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(query_params.get("end_time"), "%Y-%m-%d %H:%M:%S")
        queryset = ExecutionLog.objects.filter(biz_id=biz_id, created_at__gte=start_time, created_at__lte=end_time)
        group_result = (
            queryset.annotate(exec_date=Trunc("created_at", "day")).values("exec_date").annotate(exec_num=Count("id"))
        )
        data = []
        for item in group_result:
            data.append({"date": item["exec_date"].split(" ")[0], "value": item["exec_num"]})
        return Response({"data": data})
