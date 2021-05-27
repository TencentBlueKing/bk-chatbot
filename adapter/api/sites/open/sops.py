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
from adapter.sites.open.config.domains import SOPS_APIGATEWAY_ROOT_V2


def get_job_request_before(params):
    return params


class _SopsApi(object):
    MODULE = _("SOPS")

    def __init__(self):
        self.get_template_info = DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_template_info",
            description=_("查询单个模板详情"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_template_list = DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_template_list",
            description=_("查询模板列表"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_task_status = DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_task_status",
            description='查询任务或任务节点执行状态',
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_template_schemes_api = DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_template_schemes",
            description='查询任务或任务节点执行状态',
            module=self.MODULE,
            before_request=get_job_request_before,
        )


SopsApi = _SopsApi()
