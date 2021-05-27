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
import time

from blueapps.utils.logger import logger
from rest_framework.decorators import action
from rest_framework.response import Response

from common.generic import APIModelViewSet
from common.generic import ValidationMixin
from module_api.bk_esb.job import JOB
from module_api.iaas.http import init_views
from module_intent.constants import ONE_WEEK_SECONDS
from module_intent.control.serializers import (
    ExecutionLogSerializer,
)
from module_intent.control.throttle import IntentThrottle
from module_intent.models import ExecutionLog


class ExecutionLogViewSet(APIModelViewSet, ValidationMixin):
    """
    日志操作
    """

    queryset = ExecutionLog.objects.all()
    serializer_class = ExecutionLogSerializer
    filter_fields = {
        "biz_id": ["exact"],
        "intent_id": ["exact"],
        "intent_name": ["exact"],
        "bot_name": ["exact"],
        "bot_type": ["exact"],
        "platform": ["exact"],
        "task_id": ["exact"],
        "sender": ["exact"],
        "status": ["exact"],
    }
    ordering_fields = ["biz_id", "intent_id", "bot_type", "task_id", "sender"]
    ordering = "-updated_at"
    throttle_classes = (IntentThrottle,)

    @action(detail=False, methods=["POST"])
    def describe_logs(self, request):
        """
        获取日志
        """
        req_data, _ = init_views(request)
        data = ExecutionLog.query_log_list(**req_data["data"])
        return Response(data)

    @action(detail=False, methods=["POST"])
    def create_log(self, request):
        """
        创建日志
        """
        req_data, _ = init_views(request)
        try:
            log = ExecutionLog.create_log(**req_data["data"])
            data = {"id": log.pk}
        except Exception as e:
            logger.error(f"create_log error:{str(e)}")
            data = {}

        return Response(data)

    @action(detail=False, methods=["POST"])
    def update_log(self, request):
        """
        更新日志
        """
        req_data, _ = init_views(request)
        ExecutionLog.update_log(req_data.get("log_id", -1), **req_data["data"])
        return Response({})

    @action(detail=False, methods=["POST"])
    def describe_records(self, request):
        """
        获取平台执行记录
        """
        req_data, _ = init_views(request)
        username = req_data.get("username", "")
        biz_id = req_data.get("data", {}).get("biz_id", -1)
        end_time = int(time.time())
        start_time = end_time - ONE_WEEK_SECONDS
        response = JOB().get_job_instance_list(
            username,
            int(biz_id),
            create_time_end=end_time * 1000,
            create_time_start=start_time * 1000,
            length=10,
        )
        data = []
        if response["result"]:
            job_data = response.get("data", {}).get("data", [])
            data.extend(
                [
                    {
                        "platform": "JOB",
                        "id": item.get("job_plan_id", ""),
                        "name": item.get("name", ""),
                        "end_time": item.get("end_time", ""),
                    }
                    for item in job_data
                ],
            )

        return Response(data)
