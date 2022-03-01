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

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.response import Response

from blueapps.account.decorators import login_exempt
from common.constants import UPDATE_TASK_MAX_TIME, UPDATE_TASK_PREFIX
from common.control.throttle import ChatBotThrottle
from common.drf.view_set import BaseGetViewSet
from common.perm.permission import check_permission
from common.redis import RedisClient
from common.validation import validation
from handler.api.bk_job import JOB
from module_intent.constants import ONE_WEEK_SECONDS
from module_intent.handler.task_info import TaskDetail
from module_intent.handler.task_operation import Operation
from module_intent.handler.task_tree import Pipeline
from module_intent.models import ExecutionLog
from module_intent.proto.log import (
    ExecutionLogSerializer,
    ReqPostBotCreateLog,
    ReqPostTaskOperate,
    RspGetTaskInfoData,
    exec_log_create_apigw_docs,
    exec_log_list_apigw_docs,
    exec_task_info_apigw_docs,
    exec_task_operate_apigw_docs,
    exec_task_pipeline_apigw_docs,
    log_describe_records_docs,
    log_list_docs,
)
from module_intent.tasks.log_timer import task_status_timer


@method_decorator(name="list", decorator=log_list_docs)
@method_decorator(name="describe_records", decorator=log_describe_records_docs)
class ExecutionLogViewSet(BaseGetViewSet):
    """
    日志操作
    """

    queryset = ExecutionLog.objects.all()
    serializer_class = ExecutionLogSerializer
    filterset_class = ExecutionLog.OpenApiFilter
    throttle_classes = [ChatBotThrottle]
    ordering = "-created_at"

    @action(detail=False, methods=["POST"])
    def describe_records(self, request):
        """
        获取平台执行记录
        """
        req_data = request.payload
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
            job_data = response.get("data", {}).get("data") or []
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

        return Response({"data": data})


@method_decorator(name="list", decorator=exec_log_list_apigw_docs)
@method_decorator(name="create_log", decorator=exec_log_create_apigw_docs)
@method_decorator(name="task_info", decorator=exec_task_info_apigw_docs)
@method_decorator(name="task_pipeline", decorator=exec_task_pipeline_apigw_docs)
@method_decorator(name="task_operate", decorator=exec_task_operate_apigw_docs)
class TaskExecutionViewSet(BaseGetViewSet):
    """
    日志操作
    """

    queryset = ExecutionLog.objects.all()
    serializer_class = ExecutionLogSerializer
    filterset_class = ExecutionLog.OpenApiFilter
    throttle_classes = [ChatBotThrottle]
    ordering = "-created_at"
    # 格式化
    task_info_serializer_class = RspGetTaskInfoData  # 验证类
    task_info_valida = True  # 是否验证返回结果

    @login_exempt
    @csrf_exempt
    @check_permission()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @action(detail=False, methods=["POST"])
    @validation(ReqPostBotCreateLog)
    def create_log(self, request, *args, **kwargs):
        """
        添加机器操作日志
        """
        payload = request.payload["data"]
        log = ExecutionLog.create_log(**payload)
        data = {"id": log.pk}
        # 触发触发直接返回
        if payload.get("sender") == "trigger":
            return Response({"data": data})

        with RedisClient() as r:
            key = f"{UPDATE_TASK_PREFIX}{log.pk}"  # 唯一key
            r.set(key, 1, UPDATE_TASK_MAX_TIME)  # 设置过期时间
        return Response({"data": data})

    @action(detail=False, methods=["GET"])
    def task_info(self, request, *args, **kwargs):
        """
        获取错误信息
        """
        payload = request.payload
        ret = TaskDetail.get(payload.get("id"))
        return Response({"data": ret})

    @action(detail=False, methods=["GET"])
    def task_pipeline(self, request, *args, **kwargs):
        """
        获取执行树
        """
        payload = request.payload
        ret = Pipeline.make(payload.get("id"))
        return Response({"data": ret})

    @action(detail=False, methods=["POST"])
    @validation(ReqPostTaskOperate)
    def task_operate(self, request, *args, **kwargs):
        """
        任务操作执行
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        payload = request.payload
        id = payload.get("id")
        action = payload.get("action")
        data = payload.get("data", {})
        Operation.do(action, id, data)
        # 重新添加缓存时间
        with RedisClient() as r:
            key = f"{UPDATE_TASK_PREFIX}{id}"  # 唯一key
            r.set(key, 1, UPDATE_TASK_MAX_TIME)  # 设置过期时间
        return Response({"data": ""})

    @action(detail=False, methods=["POST"])
    def status(self, request, *args, **kwargs):
        task_status_timer()
        return Response({"data": ""})
