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

from django.utils.translation import ugettext_lazy as _

from adapter.api.base import DataAPI
from adapter.sites.open.config.domains import JOB_APIGATEWAY_ROOT_V2


def get_job_request_before(params):
    return params


class _JobApi(object):
    MODULE = _("JOB")

    def __init__(self):
        self.fast_execute_script = DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V2 + "fast_execute_script",
            description=_("快速执行脚本"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.fast_push_file = DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V2 + "fast_push_file",
            description=_("快速分发文件"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_job_instance_log = DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V2 + "get_job_instance_log",
            description=_("根据作业ID获取执行日志"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_job_list = DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V2 + "get_job_list",
            description=' 查询作业执行方案列表',
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_job_detail = DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V2 + "get_job_detail",
            description='查询执行方案详情',
            module=self.MODULE,
            before_request=get_job_request_before,
        )

JobApi = _JobApi()
