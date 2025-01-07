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
from rest_framework.response import Response
from rest_framework.decorators import action

from common.drf.validation import validation
from common.drf.view_set import BaseViewSet
from common.perm.permission import login_exempt_with_perm
from src.manager.module_notice.proto.notice import ReqPostBkMonitorDashboardGwViewSetSerializer
from src.manager.module_notice.tasks.bkm_dashboard_timer import dashboard_send


class BkMonitorDashboardGwViewSet(BaseViewSet):
    schema = None

    @login_exempt_with_perm
    @action(detail=False, methods=["POST"])
    @validation(ReqPostBkMonitorDashboardGwViewSetSerializer)
    def send(self, request, *args, **kwargs):
        dashboard_send.apply_async(kwargs={"payload": request.payload})
        return Response()
