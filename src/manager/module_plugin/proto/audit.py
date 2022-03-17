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


from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.serializers import Serializer
from module_plugin.proto import plugin_tag
from common.drf.serializers import BaseRspSerializer


# itsm回调
class ReqAuditCallBackSerializer(Serializer):
    title = serializers.CharField()
    current_status = serializers.CharField()
    sn = serializers.CharField()
    ticket_url = serializers.CharField()
    update_at = serializers.CharField()
    updated_by = serializers.CharField()
    approve_result = serializers.BooleanField()
    token = serializers.CharField()
    last_approver = serializers.CharField()


class RspAuditCallBackSerializer(BaseRspSerializer):
    pass


############################################################

audit_callback_docs = swagger_auto_schema(
    tags=plugin_tag,
    operation_id="Audit单据回调",
    request_body=ReqAuditCallBackSerializer,
    responses={
        200: RspAuditCallBackSerializer(),
    },
)
