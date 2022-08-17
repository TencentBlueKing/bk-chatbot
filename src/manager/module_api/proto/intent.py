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

from src.manager.module_api.proto import api_tag
from src.manager.module_intent.models import Intent


class IntentGWSerializer(serializers.ModelSerializer):

    # # 意图表需要
    available_user = serializers.ListField(required=False, label="可执行用户")
    available_group = serializers.ListField(required=False, label="可执行群组")
    developer = serializers.ListField(required=False, label="开发商")
    approver = serializers.ListField(required=False, label="审批人")

    class Meta:
        model = Intent
        exclude = [
            "updated_by",
            "is_deleted",
            "deleted_by",
            "deleted_at",
            "description",
        ]


intent_update_docs = swagger_auto_schema(
    tags=api_tag,
    operation_id="意图管理-修改",
    # request_body=ReqPostIntentSerializer,
)
