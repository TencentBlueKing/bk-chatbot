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
from src.manager.module_biz.proto import (
    DescribeDevopsPipelinesStartInfo,
    DescribeJob,
    DescribeSops,
    DescribeSopsSchemes,
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
