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

from adapter.api.base import BaseApi, ProxyDataAPI


class _BkITSMApi(BaseApi):
    MODULE = _("BK_ITSM")

    def __init__(self):
        self.create_ticket = ProxyDataAPI(_("创建单据"))
        self.token_verify = ProxyDataAPI(_("token校验"))
        self.ticket_approval_result = ProxyDataAPI(_("token校验"))
        self.get_services = ProxyDataAPI(_("服务列表查询"))
        self.get_service_detail = ProxyDataAPI(_("服务详情查询"))
        self.get_ticket_status = ProxyDataAPI(_("单据状态查询"))
        self.get_ticket_info = ProxyDataAPI(_("单据详情查询"))


BkITSMApi = _BkITSMApi()
