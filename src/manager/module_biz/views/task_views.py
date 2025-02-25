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

from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from common.control.throttle import ChatBotThrottle
from common.drf.generic import BaseViewSet
from common.drf.validation import validation
from common.http.request import get_request_user
from src.manager.handler.api.bk_job import JOB
from src.manager.handler.api.bk_sops import SOPS
from src.manager.handler.api.devops import DevOps
from src.manager.handler.api.bk_itsm import BkITSM
from src.manager.handler.api.bk_monitor import BkMonitor
from src.manager.module_biz.proto.task import (
    DescribeDevopsPipelinesStartInfo,
    DescribeJob,
    DescribeSops,
    DescribeSopsSchemes, SopsPreviewTaskTree,
)

tags = ["任务查询"]


class TaskViewSet(BaseViewSet):
    """
    后端任务
    """

    throttle_classes = [ChatBotThrottle]

    @swagger_auto_schema(tags=tags, operation_id="作业平台-获取JOB任务列表")
    @action(detail=False, methods=["GET"])
    def describe_jobs(self, request, **kwargs):
        """
        @api {POST} api/v1/task/{biz_id}/describe_jobs/ 获取JOB任务列表
        @apiDescription 获取JOB任务列表
        @apiName describe_jobs
        @apiGroup Task
        @apiSuccessExample {json} 返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {
                    "bk_biz_id": 1,
                    "name": "xxx",
                    "creator": "xxx",
                    "last_modify_time": xxx,
                    "create_time": xxxx,
                    "job_template_id": xxxx,
                    "id": xxxx,
                    "last_modify_user": "xxxx"
                }
            ],
            "result": true,
            "request_id": "c3705b96904142c88ab2c38681cad2b2"
        }
        """
        response = JOB().get_job_plan_list(
            get_request_user(request),
            int(kwargs.get("biz_id")),
            length=1000,
        )
        try:
            response["data"] = response["data"]["data"]
        except (KeyError, TypeError):
            pass

        return JsonResponse(response)

    @swagger_auto_schema(tags=tags, query_serializer=DescribeJob, operation_id="作业平台-获取执行方案详细信息")
    @action(detail=False, methods=["GET"])
    def describe_job(self, request, **kwargs):
        """
        @api {POST} api/v1/task/{biz_id}/describe_job/ 获取JOB任务详细信息
        @apiDescription 获取JOB任务列表
        @apiName describe_jobs
        @apiGroup Task
        @apiRequestExample {json} 请求：x
        {
           "id":123
        }
        @apiSuccessExample {json} 返回:
        {
            "message": "",
            "code": 0,
            "data": {
                job task detail info
            },
            "result": true,
            "request_id": "c3705b96904142c88ab2c38681cad2b2"
        }
        """
        response = JOB().get_job_plan_detail(
            get_request_user(request),
            int(kwargs.get("biz_id")),
            int(request.payload.get("id", -1)),
        )
        return JsonResponse(response)

    @swagger_auto_schema(tags=tags, operation_id="标准运维-获取任务列表")
    @action(detail=False, methods=["GET"])
    def describe_sopss(self, request, **kwargs):
        """
        @api {POST} api/v1/task/{biz_id}/describe_sopss/ 获取标准运维任务列表
        @apiDescription 获取标准运维任务列表
        @apiName describe_sopss
        @apiGroup Task
        @apiSuccessExample {json} 返回:
        {
            "message": "",
            "code": 0,
            "data": [
                {}
            ],
            "result": true,
            "request_id": "c3705b96904142c88ab2c38681cad2b2"
        }
        """
        response = SOPS().get_template_list(
            get_request_user(request),
            int(kwargs.get("biz_id")),
        )
        return JsonResponse(response)

    @swagger_auto_schema(tags=tags, query_serializer=DescribeSops, operation_id="标准运维-获取任务明细")
    @action(detail=False, methods=["GET"])
    @validation(DescribeSops)
    def describe_sops(self, request, **kwargs):
        """
        @api {POST} api/v1/task/{biz_id}/describe_sops/ 获取标准运维任务明细
        @apiDescription 获取标准运维任务明细
        @apiName describe_sops
        @apiGroup Task
        @apiRequestExample {json} 请求：
        {
            "id":123
        }
        @apiSuccessExample {json} 返回:
        {
            "message": "",
            "code": 0,
            "data": {
                sop task detail info
            },
            "result": true,
            "request_id": "c3705b96904142c88ab2c38681cad2b2"
        }
        """
        response = SOPS().get_template_info(
            get_request_user(request),
            int(kwargs.get("biz_id")),
            int(request.payload.get("id", -1)),
        )
        return JsonResponse(response)

    @swagger_auto_schema(tags=tags, query_serializer=SopsPreviewTaskTree(), operation_id="预览模板创建后生成的任务")
    @action(detail=False, methods=["POST"])
    @validation(SopsPreviewTaskTree)
    def sops_preview_task_tree(self, request, **kwargs):
        """
        预览模板创建后生成的任务树
        """
        response = SOPS().preview_task_tree(
            get_request_user(request),
            kwargs.get("biz_id"),
            request.payload.get("template_id"),
            request.payload.get("exclude_task_nodes_id")
        )
        return JsonResponse(response)

    @swagger_auto_schema(tags=tags, query_serializer=DescribeSopsSchemes, operation_id="标准运维-获取任务分组信息")
    @action(detail=False, methods=["GET"])
    @validation(DescribeSopsSchemes)
    def describe_sops_schemes(self, request, **kwargs):
        """

        @api {POST} api/v1/task/{biz_id}/describe_sops_schemes/ 获取标准运维任务分组信息
        @apiDescription 获取标准运维任务分组信息
        @apiName describe_sops_schemes
        @apiGroup Task
        @apiRequestExample {json} 请求：
        {
            "id":123
        }
        @apiSuccessExample {json} 返回:
        {
            "message": "",
            "code": 0,
            "data": {
                sop sops_scheme detail info
            },
            "result": true,
            "request_id": "c3705b96904142c88ab2c38681cad2b2"
        }
        """
        response = SOPS().get_template_schemes(
            int(kwargs.get("biz_id")),
            int(request.payload.get("id", -1)),
        )
        return JsonResponse(response)

    @swagger_auto_schema(tags=tags, operation_id="蓝盾-查看项目")
    @action(detail=False, methods=["GET"])
    def describe_devops_projects(self, request, **kwargs):
        """
        查询蓝盾流水线
        """
        response = DevOps.app_project_list(get_request_user(request))
        return Response(response.get("data", []))

    @swagger_auto_schema(tags=tags, operation_id="蓝盾-查询流水线")
    @action(detail=False, methods=["GET"])
    def describe_devops_pipelines(self, request, **kwargs):
        """
        查询蓝盾流水线
        """
        response = DevOps.app_pipeline_list(
            get_request_user(request),
            project_id=kwargs.get("biz_id"),
        )
        return Response(response.get("data", []))

    @swagger_auto_schema(tags=tags, query_serializer=DescribeDevopsPipelinesStartInfo, operation_id="蓝盾-查看启动详情")
    @action(detail=False, methods=["GET"])
    @validation(DescribeDevopsPipelinesStartInfo)
    def describe_devops_pipelines_params(self, request, **kwargs):
        """
        蓝盾-查看启动详情
        """
        response = DevOps.app_build_start_info(
            get_request_user(request),
            project_id=kwargs.get("biz_id"),
            pipeline_id=request.payload.get("pipeline_id"),
        )
        return Response(response.get("data", []))

    @swagger_auto_schema(tags=tags, operation_id="ITSM-查询服务列表")
    @action(detail=False, methods=["GET"])
    def describe_itsm_services(self, request, **kwargs):
        """
        ITSM-查询服务列表
        """
        response = BkITSM.get_services()
        return Response(response.get("data", []))

    @swagger_auto_schema(tags=tags, operation_id="ITSM-查询服务详情")
    @action(detail=False, methods=["GET"])
    def describe_itsm_service(self, request, **kwargs):
        """
        ITSM-查询服务详情
        """
        service_id = request.query_params.get("service_id")
        response = BkITSM.get_service_detail(service_id)
        return Response(response.get("data", []))

    @swagger_auto_schema(tags=tags, operation_id="BkMonitor-查询仪表盘目录树")
    @action(detail=False, methods=["GET"])
    def describe_bkmonitor_dashboards(self, request, biz_id, **kwargs):
        """
        BKMONITOR-查询仪表盘目录树
        """
        result = BkMonitor.get_dashboard_directory_tree(biz_id)
        data = []
        for c in result:
            _dashboards = [{"title": f"{c['title']}/{d['title']}", "uid": d["uid"]} for d in c["dashboards"]]
            data.extend(_dashboards)
        return Response(data)

    @swagger_auto_schema(tags=tags, operation_id="BkMonitor-查询仪表盘详情")
    @action(detail=False, methods=["GET"])
    def describe_bkmonitor_dashboard(self, request, biz_id, **kwargs):
        """
        BkMonitor-查询仪表盘详情
        """
        dashboard_uid = request.query_params.get("dashboard_uid")
        result = BkMonitor.get_dashboard_detail(biz_id, dashboard_uid)
        dashboard_info = json.loads(result["data"])
        panels = BkMonitor.get_all_panels(dashboard_info.get("panels", []))
        variables = []
        for t in dashboard_info.get("templating", {}).get("list", []):
            variables.append({
                "key": t["name"],
                "name": f"[仪表盘变量]{t['name']}",
                "tips": f"如需自定义{t['name']}，请将<[通用]使用仪表盘变量默认值>设置为否",
                "default": "使用仪表盘变量默认值"
            })

        variables.extend([
            {
                "key": "__sys__use_dashboard_default",
                "name": "[通用]使用仪表盘变量默认值",
                "tips": "如果使用仪表盘变量默认值，则无须设置仪表盘变量，将以蓝鲸监控仪表盘默认值为准",
                "default": "是"
            },
            {
                "key": "__sys__width",
                "name": "[通用]宽度",
                "tips": "请设置图片宽度, 单位px",
                "default": 800,
            },
            {
                "key": "__sys__to_now_hours",
                "name": "[通用]时间范围",
                "tips": "请设置查看最近几小时的仪表盘",
                "default": 6,
            },
            {
                "key": "__sys__scale",
                "name": "[通用]像素密度",
                "tips": "请设置图片像素密度，默认2, 最大4, 越大越清晰，但是图片大小也越大",
                "default": 2,
            },
            {
                "key": "__sys__height",
                "name": "[通用]高度",
                "tips": "仅在panel_id不为空时有效",
                "default": 500,
            }

        ])
        data = {
            "variables": variables,
            "panels": panels,
        }
        return Response(data)
