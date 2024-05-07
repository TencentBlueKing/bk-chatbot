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
from config.domains import BK_ITSM_APIGW


class _BkITSMApi:
    MODULE = _("BK_ITSM")

    @property
    def create_ticket(self):
        return DataAPI(
            method="POST",
            url=BK_ITSM_APIGW + "create_ticket",
            description=_("创建单据"),
            module=self.MODULE,
        )

    @property
    def token_verify(self):
        return DataAPI(
            method="POST",
            url=BK_ITSM_APIGW + "token/verify/",
            description=_("token校验"),
            module=self.MODULE,
        )

    @property
    def ticket_approval_result(self):
        return DataAPI(
            method="POST",
            url=BK_ITSM_APIGW + "ticket_approval_result/",
            description=_("获取审核单据结果"),
            module=self.MODULE,
        )

    @property
    def get_services(self):
        return DataAPI(
            method="GET",
            url=BK_ITSM_APIGW + "get_services/",
            description=_("服务列表查询"),
            module=self.MODULE,
        )

    @property
    def get_service_detail(self):
        return DataAPI(
            method="GET",
            url=BK_ITSM_APIGW + "get_service_detail/",
            description=_("服务详情查询"),
            module=self.MODULE,
        )

    @property
    def get_ticket_status(self):
        return DataAPI(
            method="GET",
            url=BK_ITSM_APIGW + "get_ticket_status/",
            description=_("单据状态查询"),
            module=self.MODULE,
        )

    @property
    def get_ticket_info(self):
        return DataAPI(
            method="GET",
            url=BK_ITSM_APIGW + "get_ticket_info/",
            description=_("单据详情查询"),
            module=self.MODULE,
        )
