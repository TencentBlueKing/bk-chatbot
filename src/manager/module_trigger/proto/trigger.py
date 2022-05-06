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

from common.drf.serializers import BaseRspSerializer
from src.manager.module_trigger.models import TriggerModel

trigger_tag = ["触发器"]


class TriggerViewSerializer(serializers.ModelSerializer):
    """
    语料领域验证器
    """

    info = serializers.DictField(label="触发器key")

    class Meta:
        model = TriggerModel
        fields = [
            "id",
            "name",
            "platform",
            "trigger_key",
            "trigger_type",
            "info",
            "created_by",
            "created_at",
            "updated_at",
        ]


# 查询响应
class RspListTriggerSerializer(BaseRspSerializer):
    count = serializers.IntegerField(label="数量")
    data = serializers.ListField(child=TriggerViewSerializer())


# 添加响应
class RspCreateTriggerSerializer(BaseRspSerializer):
    data = TriggerViewSerializer()


#######################################

trigger_list_docs = swagger_auto_schema(
    tags=trigger_tag,
    operation_id="触发器-查询",
    responses={200: RspListTriggerSerializer()},
)

trigger_create_docs = swagger_auto_schema(
    tags=trigger_tag,
    operation_id="触发器-添加",
    responses={200: RspListTriggerSerializer()},
)

trigger_update_docs = swagger_auto_schema(
    tags=trigger_tag,
    operation_id="触发器-修改",
    responses={200: BaseRspSerializer()},
)

trigger_delete_docs = swagger_auto_schema(
    tags=trigger_tag,
    operation_id="触发器-删除",
    responses={200: BaseRspSerializer()},
)
