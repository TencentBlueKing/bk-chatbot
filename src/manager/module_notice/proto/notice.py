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
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers

from common.drf.field import BizId, DefaultFiled
from src.manager.module_notice.models import NoticeGroupModel, TriggerModel
from src.manager.module_notice.proto import notice_tag
from common.constants import TAK_PLATFORM_JOB, TAK_PLATFORM_SOPS


class DefaultTriggerName(DefaultFiled):
    def set_context(self, instance):
        """
        设置默认值
        """
        request = instance.context["request"]
        payload = request.payload
        # 设置默认值
        trigger_id = payload.get("trigger_id")
        try:
            trigger_obj = TriggerModel.objects.get(pk=trigger_id)
        except ObjectDoesNotExist:
            raise ValueError(f"不存在ID为{trigger_id}的触发器")
        setattr(self, self.attribute_name, trigger_obj.name)


class NoticeGroupViewSerializer(serializers.ModelSerializer):
    """
    查询所用的协议
    """

    group_value = serializers.ListField(required=False, default=[], label="审批人")

    class Meta:
        model = NoticeGroupModel
        fields = [
            "id",
            "biz_id",
            "name",
            "trigger_id",
            "trigger_name",
            "group_type",
            "group_value",
            "description",
            "created_by",
            "created_at",
        ]


class NoticeGroupViewGWSerializer(serializers.ModelSerializer):
    """
    查询所用的协议
    """

    class Meta:
        model = NoticeGroupModel
        fields = ["id", "biz_id", "name"]


class ReqGetNoticeGroupGWViewSerializer(serializers.Serializer):
    """
    查询协议
    """

    biz_id = serializers.CharField(label="业务ID")


class ReqPostNoticeGroupViewSerializer(NoticeGroupViewSerializer):
    """
    添加协议
    """

    biz_id = serializers.HiddenField(default=BizId())
    trigger_name = serializers.HiddenField(default=DefaultTriggerName())


class ReqPutNoticeGroupViewSerializer(NoticeGroupViewSerializer):
    """
    修改协议
    """

    trigger_name = serializers.HiddenField(default=DefaultTriggerName())

    class Meta:
        model = NoticeGroupModel
        fields = ["name", "trigger_id", "trigger_name", "group_type", "group_value", "description"]


class ReqPostNoticeGroupSendMsgGWViewSerializer(serializers.Serializer):
    """
    用户组发送通知协议
    """

    notice_group_id_list = serializers.ListField()
    msg_type = serializers.ChoiceField(choices=["text", "markdown"], default="text")
    msg_content = serializers.CharField()


class ReqPostTaskBroadStratGWViewSerializer(serializers.Serializer):
    """
    请求任务播报开始协议
    """

    operator = serializers.CharField(label="操作人")
    biz_id = serializers.IntegerField(label="业务ID")
    task_id = serializers.IntegerField(label="播报任务ID")
    platform = serializers.ChoiceField(label="任务所属平台", choices=[TAK_PLATFORM_JOB, TAK_PLATFORM_SOPS])
    session_info = serializers.CharField(label="触发播报的会话ID", required=False, default={})
    share_group_list = serializers.ListField(label="分享播报用户通知组列表", required=False, default=[])


class ReqPostTaskBroadShareGWViewSerializer(serializers.Serializer):
    """
    分享播报协议
    """

    share_group_list = serializers.ListField(label="分享播报用户通知组列表")


class ReqPostNoticeSendWebhookGWViewSerializer(serializers.Serializer):
    """
    用户组发送通知协议
    """

    msg_type = serializers.ChoiceField(choices=["text", "markdown"], default="text")
    msg_content = serializers.CharField()


#######################################


notice_group_list_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="群组-查询",
)

notice_group_create_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="群组-添加",
)

notice_group_update_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="群组-修改",
)

notice_group_delete_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="群组-删除",
)

notice_group_retrieve_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="群组-单个",
    responses={},
)
