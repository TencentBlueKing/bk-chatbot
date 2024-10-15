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
import time

from django.utils.decorators import method_decorator
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response

from common.constants import TASK_EXECUTE_STATUS_DICT, TaskExecStatus
from common.control.throttle import ChatBotThrottle
from common.drf.validation import validation
from common.drf.view_set import BaseGetViewSet
from common.perm.permission import login_exempt_with_perm
from common.redis import RedisClient
from src.manager.handler.api.bk_job import JOB
from src.manager.handler.api.bk_sops import SOPS
from src.manager.module_intent.constants import ONE_WEEK_SECONDS, UPDATE_TASK_MAX_TIME, UPDATE_TASK_PREFIX
from src.manager.module_intent.handler.task_info import TaskDetail
from src.manager.module_intent.handler.task_operation import Operation
from src.manager.module_intent.handler.task_tree import Pipeline
from src.manager.module_intent.models import ExecutionLog
from src.manager.module_intent.models import Intent
from src.manager.module_intent.proto.log import (
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

BKAPP_JOB_HOST = os.getenv("BKAPP_JOB_HOST", "")
BKAPP_DEVOPS_HOST = os.getenv("BKAPP_DEVOPS_HOST", "")
BKAPP_SOPS_HOST = os.getenv("BKAPP_SOPS_HOST", "")


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

    def list(self, request, *args, **kwargs):
        username = request.user.username
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.make_task_url(username, serializer.data)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = self.make_task_url(username, serializer.data)
        return Response(data)

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

    @staticmethod
    def make_task_url(username, task_data):
        result = SOPS().get_user_project_list(username)
        sop_biz_project_map = {}
        if result["result"]:
            sop_biz_project_map = {item["bk_biz_id"]: item["project_id"] for item in result["data"]}

        data = []
        for item in task_data:
            task_url = ""
            if item["platform"] == ExecutionLog.PlatformType.SOPS.value:
                project_id = sop_biz_project_map.get(item["biz_id"])
                if project_id:
                    task_url = "{}/taskflow/execute/{}/?instance_id={}".format(
                        BKAPP_SOPS_HOST, project_id, item["task_id"]
                    )
                else:
                    task_url = None
            if item["platform"] == ExecutionLog.PlatformType.JOB.value:
                task_url = "{}/biz/{}/execute/task/{}".format(BKAPP_JOB_HOST, item["biz_id"], item["task_id"])
            if item["platform"] == ExecutionLog.PlatformType.DEV_OPS.value:
                task_url = "{}/console/pipeline/{}/{}/detail/{}".format(
                    BKAPP_DEVOPS_HOST,
                    item["project_id"],
                    item["feature_id"],
                    item["task_id"],
                )
            data.append({"task_url": task_url, **item})
        return data


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

    @login_exempt_with_perm
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @action(detail=False, methods=["GET"])
    def my_task_list(self, request, *args, **kwargs):
        """
        获取我的任务列表
        """
        operator = request.query_params.get("operator")
        biz_id = request.query_params.get("biz_id")
        intent_id_list = Intent.objects.filter(
            (Q(available_user__contains="all") | Q(available_user__contains=operator)) & Q(biz_id=biz_id)
        ).values_list('id', flat=True)

        execution_queryset = ExecutionLog.objects.filter(
            intent_id__in=intent_id_list,
            status__in=[TaskExecStatus.RUNNING.value, TaskExecStatus.FAIL.value, TaskExecStatus.SUSPENDED.value]
        ).order_by('-created_at')[:15]
        serializer = ExecutionLogSerializer(execution_queryset, many=True)
        return Response({"data": serializer.data})

    @action(detail=False, methods=["POST"])
    @validation(ReqPostBotCreateLog)
    def create_log(self, request, *args, **kwargs):
        """
        添加机器操作日志
        """
        payload = request.payload["data"]
        log = ExecutionLog.create_log(**payload)
        data = {
            "id": log.pk,
            "task_uuid": log.task_uuid,
        }

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
        action = int(payload.get("action"))
        data = payload.get("data", {})
        Operation.do(action, id, data)
        # 重新添加缓存时间
        with RedisClient() as r:
            key = f"{UPDATE_TASK_PREFIX}{id}"  # 唯一key
            r.set(key, 1, UPDATE_TASK_MAX_TIME)  # 设置过期时间
        return Response({"data": ""})

    @action(detail=False, methods=["GET"], url_name="status", url_path=r"status/(?P<uuid>\w+)")
    def status(self, request, *args, **kwargs):
        """
        通过UUID查询执行状态
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        task_uuid = kwargs.get("uuid")
        execution_log = ExecutionLog.query_log(
            **{
                "task_uuid": task_uuid,
            }
        )
        return Response(
            {
                "data": {
                    "status": execution_log.status,
                    "message": TASK_EXECUTE_STATUS_DICT.get(execution_log.status),
                    "l_message": ExecutionLog.TaskExecStatus(execution_log.status).name,
                }
            }
        )
