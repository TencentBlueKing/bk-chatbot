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
import datetime

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from common.drf.generic import BaseViewSet
from common.http.request import batch_request
from common.utils.batch import batch_exec_func
from common.constants import (
    TAK_PLATFORM_JOB,
    TAK_PLATFORM_SOPS,
    TAK_PLATFORM_DEVOPS,
    TASK_EXECUTE_STATUS_DICT,
    TASK_EXEC_STATUS_COLOR_DICT,
)
from src.manager.handler.api.bk_job import JOB, job_instance_status_map
from src.manager.handler.api.bk_sops import SOPS, sops_instance_status_map
from src.manager.module_intent.models import ExecutionLog
from common.perm.permission import login_exempt_with_perm
from src.manager.module_biz.handlers.platform_task import parse_sops_pipeline_tree, parse_job_task_tree
from common.drf.validation import validation
from src.manager.module_biz.proto.exec_task import (
    ExecTaskListParamsSerializer,
    ExecTaskDetailParamsSerializer,
    ExecTaskParamsParamsSerializer,
)

tags = ["执行任务查询"]
BKAPP_JOB_HOST = os.getenv("BKAPP_JOB_HOST", "")
BKAPP_DEVOPS_HOST = os.getenv("BKAPP_DEVOPS_HOST", "")


class ExecTaskViewSet(BaseViewSet):
    """
    当前业务在标准运维、作业平台、蓝盾执行的任务
    """

    @login_exempt_with_perm
    @validation(ExecTaskListParamsSerializer)
    @swagger_auto_schema(tags=tags, operation_id="apigw获取当前业务下的执行任务列表")
    @action(detail=False, methods=["GET"])
    def task_list(self, request, **kwargs):
        # 参数获取
        biz_id = int(kwargs.get("biz_id"))
        operator = request.query_params.get("operator")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("pagesize", 10))

        # 查询两天内各平台任务执行记录
        now = datetime.datetime.now()
        two_days_ago = now + datetime.timedelta(days=-2)

        # 转换job时间参数
        job_end_time = int(now.timestamp() * 1000)
        job_start_time = int(two_days_ago.timestamp() * 1000)

        # 获取标准运维的任务ID列表
        result = SOPS().get_task_list(operator, biz_id, limit=50)
        sops_task_id_list = [task["id"] for task in result["data"]]

        # 多线程获取各平台任务列表
        func_info_list = [
            {
                "func": batch_request,
                "params": {
                    "func": JOB().get_job_instance_list,
                    "params": {
                        "bk_username": operator,
                        "bk_biz_id": biz_id,
                        "create_time_start": job_start_time,
                        "create_time_end": job_end_time,
                        "launch_mode": 1,
                    },
                    "get_data": lambda x: x["data"]["data"],
                    "get_count": lambda x: x["data"]["total"],
                },
                "data_key": "job_manual_task",
            },
            {
                "func": batch_request,
                "params": {
                    "func": JOB().get_job_instance_list,
                    "params": {
                        "bk_username": operator,
                        "bk_biz_id": biz_id,
                        "create_time_start": job_start_time,
                        "create_time_end": job_end_time,
                        "launch_mode": 2,
                    },
                    "get_data": lambda x: x["data"]["data"],
                    "get_count": lambda x: x["data"]["total"],
                },
                "data_key": "job_api_task",
            },
            {
                "func": SOPS().get_tasks_status,
                "params": {"bk_username": operator, "bk_biz_id": biz_id, "task_id_list": sops_task_id_list},
                "data_key": "sops_result",
            },
            {
                "func": ExecutionLog.objects.filter,
                "params": {
                    "biz_id": biz_id,
                    "platform": ExecutionLog.PlatformType.DEV_OPS.value,
                    "created_at__gt": two_days_ago,
                },
                "data_key": "devops_queryset",
            },
        ]
        batch_result = batch_exec_func(func_info_list)

        total_task_list = []

        # 处理job的执行历史
        job_task_list = (batch_result["job_manual_task"] or []) + (batch_result["job_api_task"] or [])
        for task in job_task_list:
            total_task_list.append(
                {
                    "task_name": "[作业平台] {}".format(task["name"]),
                    "task_status": TASK_EXECUTE_STATUS_DICT[job_instance_status_map[task["status"]]],
                    "task_status_color": TASK_EXEC_STATUS_COLOR_DICT[job_instance_status_map[task["status"]]],
                    "task_platform": TAK_PLATFORM_JOB,
                    "task_id": task["job_instance_id"],
                    "create_time": task["create_time"],
                    "task_url": "{}/biz/{}/execute/task/{}".format(BKAPP_JOB_HOST, biz_id, task.get("job_instance_id")),
                }
            )

        # 处理标准运维的任务状态
        sops_task_list = batch_result["sops_result"]["data"]
        for task in sops_task_list:
            total_task_list.append(
                {
                    "task_name": "[标准运维] {}".format(task["name"]),
                    "task_status": TASK_EXECUTE_STATUS_DICT[sops_instance_status_map[task["status"]["state"]]],
                    "task_status_color": TASK_EXEC_STATUS_COLOR_DICT[sops_instance_status_map[task["status"]["state"]]],
                    "task_platform": TAK_PLATFORM_SOPS,
                    "task_id": task["id"],
                    "task_url": task["url"],
                    "create_time": datetime.datetime.strptime(
                        task["create_time"], "%Y-%m-%d %H:%M:%S +0800"
                    ).timestamp()
                    * 1000,
                }
            )

        # 处理技能触发的蓝盾任务
        devops_queryset = batch_result["devops_queryset"]
        for task in devops_queryset:
            total_task_list.append(
                {
                    "task_name": f"[蓝盾] {task.intent_name}",
                    "task_status": TASK_EXECUTE_STATUS_DICT[task.status],
                    "task_status_color": TASK_EXEC_STATUS_COLOR_DICT[task.status],
                    "task_platform": TAK_PLATFORM_DEVOPS,
                    "task_id": task.id,
                    "create_time": datetime.datetime.strptime(task.created_at, "%Y-%m-%d %H:%M:%S").timestamp() * 1000,
                    "task_url": "{}/console/pipeline/{}/{}/detail/{}".format(
                        BKAPP_DEVOPS_HOST, task.project_id, task.feature_id, task.task_id
                    ),
                }
            )

        total_task_list = sorted(total_task_list, key=lambda x: x["create_time"], reverse=True)

        # 分页数据处理
        start = (page - 1) * page_size
        end = start + page_size
        data = {"count": len(total_task_list), "data": total_task_list[start:end]}

        return Response(data)

    @login_exempt_with_perm
    @validation(ExecTaskDetailParamsSerializer)
    @swagger_auto_schema(tags=tags, operation_id="apigw获取执行任务详情")
    @action(detail=True, methods=["GET"])
    def task_detail(self, request, pk, **kwargs):
        operator = request.query_params.get("operator")
        biz_id = int(kwargs.get("biz_id"))
        platform = request.query_params.get("platform")
        is_parse_all = request.query_params.get("is_parse_all", "0") == "1"
        task_id = pk

        if platform == TAK_PLATFORM_JOB:
            task_info = JOB().get_job_instance_status(operator, biz_id, task_id).get("data")
            parse_result = parse_job_task_tree(task_info, is_parse_all)

        if platform == TAK_PLATFORM_SOPS:
            task_info = SOPS().get_task_detail(operator, biz_id, task_id)
            status_info = SOPS().get_task_status(operator, biz_id, task_id).get("data")
            parse_result = parse_sops_pipeline_tree(task_info, status_info, is_parse_all)

        parse_result.update({"start_user": operator})

        return Response(parse_result)

    @login_exempt_with_perm
    @validation(ExecTaskParamsParamsSerializer)
    @swagger_auto_schema(tags=tags, operation_id="apigw获取执行任务参数")
    @action(detail=True, methods=["GET"])
    def task_params(self, request, pk, **kwargs):
        operator = request.query_params.get("operator")
        biz_id = int(kwargs.get("biz_id"))
        platform = request.query_params.get("platform")
        task_id = pk

        if platform == TAK_PLATFORM_JOB:
            params_info = JOB().get_job_instance_global_var_value(operator, biz_id, task_id)
            task_info = JOB().get_job_instance_status(operator, biz_id, task_id).get("data")
            job_instance_id = params_info.get("job_instance_id")
            step_instance_var_list = params_info.get("step_instance_var_list", [])
            params_result = {}
            global_var_list = [var for s in step_instance_var_list for var in s["global_var_list"]]
            for var in global_var_list:
                params_result.update({var["name"]: {"params_name": var["name"], "params_value": var["value"]}})

            data = {
                "task_url": f"{BKAPP_JOB_HOST}/biz/{biz_id}/execute/task/{job_instance_id}",
                "task_name": "[作业平台] {}".format(task_info.get("job_instance").get("name")),
                "params": list(params_result.values()),
            }

        if platform == TAK_PLATFORM_SOPS:
            task_info = SOPS().get_task_detail(operator, biz_id, task_id)
            constants = task_info.get("constants")
            params_result = [
                {"params_name": v["name"], "params_value": v["value"]}
                for k, v in constants.items()
                if v["show_type"] == "show"
            ]
            data = {
                "task_url": task_info.get("task_url"),
                "task_name": "[标准运维] {}".format(task_info.get("name")),
                "params": params_result,
            }

        return Response(data)
