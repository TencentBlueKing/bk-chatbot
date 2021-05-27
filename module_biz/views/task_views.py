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
from django.http import JsonResponse
from rest_framework.decorators import action

from common.generic import APIModelViewSet
from common.generic import ValidationMixin
from common.utils.users import get_request_user
from module_api.bk_esb.job import JOB
from module_api.bk_esb.sops import SOPS
from module_api.iaas.http import init_views
from module_biz.control.permission import BizPermission
from module_biz.control.throttle import BizThrottle


class TaskViewSet(APIModelViewSet, ValidationMixin):
    """
    后端任务
    """

    permission_classes = (BizPermission,)
    throttle_classes = (BizThrottle,)

    @action(detail=True, methods=["POST"])
    def describe_jobs(self, request, pk):
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
            get_request_user(request), int(pk), length=1000
        )
        return JsonResponse(response)

    @action(detail=True, methods=["POST"])
    def describe_job(self, request, pk):
        """
        @api {POST} api/v1/task/{biz_id}/describe_job/ 获取JOB任务详细信息
        @apiDescription 获取JOB任务列表
        @apiName describe_jobs
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
                job task detail info
            },
            "result": true,
            "request_id": "c3705b96904142c88ab2c38681cad2b2"
        }
        """
        req_data, _ = init_views(request)
        response = JOB().get_job_plan_detail(
            get_request_user(
                request,
            ),
            int(pk),
            int(req_data.get("id", -1)),
        )
        return JsonResponse(response)

    @action(detail=True, methods=["POST"])
    def describe_sopss(self, request, pk):
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
        response = SOPS().get_template_list(get_request_user(request), int(pk))
        return JsonResponse(response)

    @action(detail=True, methods=["POST"])
    def describe_sops(self, request, pk):
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
        req_data, _ = init_views(request)
        response = SOPS().get_template_info(
            get_request_user(
                request,
            ),
            int(pk),
            int(req_data.get("id", -1)),
        )
        return JsonResponse(response)

    @action(detail=True, methods=["POST"])
    def describe_sops_schemes(self, request, pk):
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
        req_data, _ = init_views(request)
        response = SOPS().get_template_schemes(
            int(pk),
            int(req_data.get("id", -1)),
        )
        return JsonResponse(response)
