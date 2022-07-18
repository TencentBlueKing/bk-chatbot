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

from common.drf.serializers import BaseRspSerializer
from src.manager.module_intent.models import Intent
from src.manager.module_intent.proto import intent_tag


class IntentSerializer(serializers.ModelSerializer):

    # 意图表需要
    available_user = serializers.ListField(required=True, label="可执行用户")
    available_group = serializers.ListField(required=True, label="可执行群组")
    developer = serializers.ListField(required=False, default=[], label="开发商")
    approver = serializers.ListField(required=False, default=[], label="审批人")

    class Meta:
        model = Intent
        exclude = [
            "updated_by",
            "is_deleted",
            "deleted_by",
            "deleted_at",
            "description",
        ]


class ReqGetIntentSerializer(serializers.ModelSerializer):
    # 意图表需要
    available_user = serializers.ListField(required=True, label="可执行用户")
    available_group = serializers.ListField(required=True, label="可执行群组")
    developer = serializers.ListField(required=False, default=[], label="开发商")
    approver = serializers.ListField(required=False, default=[], label="审批人")

    class Meta:
        model = Intent
        exclude = [
            "updated_by",
            "is_deleted",
            "deleted_by",
            "deleted_at",
            "description",
        ]


class ReqPostIntentSerializer(Serializer):
    # 意图表需要
    available_user = serializers.ListField(required=True, label="可执行用户")
    available_group = serializers.ListField(required=True, label="可执行群组")
    developer = serializers.ListField(required=False, default=[], label="开发商")
    approver = serializers.ListField(required=False, default=[], label="审批人")
    is_commit = serializers.BooleanField(required=True, label="执行确认")
    notice_discern_success = serializers.BooleanField(required=True, label="识别成功通知")
    notice_start_success = serializers.BooleanField(required=True, label="启动成功通知")
    notice_exec_success = serializers.BooleanField(required=True, label="启动成功通知")
    # 其余表需要
    utterances = serializers.ListField(label="语料信息")

    # task表数据
    platform = serializers.CharField(label="平台类型")
    task_id = serializers.CharField(label="任务id")
    source = serializers.DictField(label="数据源数据")
    slots = serializers.ListField(label="槽位信息", allow_null=True)
    serial_number = serializers.CharField(label="序列号")
    activities = serializers.ListField(label="节点信息")
    project_id = serializers.CharField(label="项目id")
    script = serializers.CharField(label="脚本信息")


class ReqPostFetchIntentCountSerializers(Serializer):
    pass


class RsqPostFetchIntentCountSerializers(BaseRspSerializer):
    """
    查看意图数量响应
    """

    class RsqPostFetchIntentCountSerializersData(Serializer):
        count = serializers.IntegerField(label="意图数量")

    data = RsqPostFetchIntentCountSerializersData()


############################################################

intent_list_docs = swagger_auto_schema(
    tags=intent_tag,
    operation_id="意图管理-获取",
    # responses={200: RspListPluginSerializer()},
)
intent_create_docs = swagger_auto_schema(
    tags=intent_tag,
    operation_id="意图管理-添加",
    request_body=ReqPostIntentSerializer,
    # responses={200: RspListPluginSerializer()},
)
intent_update_docs = swagger_auto_schema(
    tags=intent_tag,
    operation_id="意图管理-修改",
    request_body=ReqPostIntentSerializer,
    # responses={200: RspListPluginSerializer()},
)
intent_del_docs = swagger_auto_schema(
    tags=intent_tag,
    operation_id="意图管理-删除",
    # responses={200: RspListPluginSerializer()},
)

intent_count_docs = swagger_auto_schema(
    tags=intent_tag,
    operation_id="意图管理-数量查询",
    request_body=ReqPostFetchIntentCountSerializers(),
    responses={200: RsqPostFetchIntentCountSerializers()},
)
