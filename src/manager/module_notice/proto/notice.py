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

from common.constants import TAK_PLATFORM_DEVOPS, TAK_PLATFORM_JOB, TAK_PLATFORM_SOPS
from common.drf.field import BizId, DefaultFiled
from common.drf.serializers import BaseRspSerializer
from src.manager.module_notice.models import NoticeGroupModel, TriggerModel
from src.manager.module_notice.proto import notice_tag


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
            "updated_by",
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
    msg_content = serializers.CharField(default="")
    msg_param = serializers.DictField(default={})


class ChatReplyGWViewSerializer(serializers.Serializer):
    """
    闲聊接口调用协议
    """

    chat_content = serializers.CharField()


class ReqPostTaskBroadStratGWViewSerializer(serializers.Serializer):
    """
    请求任务播报开始协议
    """

    operator = serializers.CharField(label="操作人")
    biz_id = serializers.IntegerField(label="业务ID")
    task_id = serializers.IntegerField(label="播报任务ID")
    platform = serializers.ChoiceField(
        label="任务所属平台", choices=[TAK_PLATFORM_JOB, TAK_PLATFORM_SOPS, TAK_PLATFORM_DEVOPS]
    )
    session_info = serializers.JSONField(label="触发播报的会话ID", required=False, default={})
    extra_notice_info = serializers.ListField(label="使用bkchat通知的附加通知人和群组", required=False, default=[])
    share_group_list = serializers.ListField(label="分享播报用户通知组列表", required=False, default=[])
    ladder_list = serializers.ListField(label="播报的时间阶梯", default=[5, 10, 20, 40, 60])

    is_devops_plugin = serializers.BooleanField(label="是否来自蓝盾插件启动播报", required=False, default=False)
    devops_project_id = serializers.CharField(label="蓝盾项目ID", required=False)
    devops_pipeline_id = serializers.CharField(label="蓝盾流水线ID", required=False)
    devops_build_id = serializers.CharField(label="蓝盾构建ID", required=False)


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


class ReqGetNoticeLogViewSerializer(serializers.Serializer):
    """
    日志查询请求协议
    """

    page = serializers.IntegerField(label="页码")
    pagesize = serializers.IntegerField(label="每页数据")
    send_result = serializers.ChoiceField(label="消息结果", required=False, choices=["true", "false"])
    msg_source = serializers.CharField(label="消息来源", required=False)
    im_platform = serializers.CharField(label="im平台", required=False)
    raw_data = serializers.CharField(label="", required=False)


class RspGetNoticeLogViewSerializer(BaseRspSerializer):
    """
    日志查询响应协议
    """

    class RspGetNoticeLogData(serializers.Serializer):
        biz_id = serializers.IntegerField(label="业务ID")
        biz_name = serializers.CharField(label="业务名称")
        msg_data = serializers.CharField(label="消息数据")
        send_time = serializers.CharField(label="发送时间")
        send_result = serializers.CharField(label="发送结果")
        msg_source = serializers.CharField(label="消息来源")
        group_name = serializers.CharField(label="发送群组名称")
        msg_type = serializers.CharField(label="消息类型")
        im_platform = serializers.CharField(label="平台类型")
        raw_data = serializers.CharField(label="原始数据")

    data = RspGetNoticeLogData()


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

notice_log_list_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="日志-查询",
    query_serializer=ReqGetNoticeLogViewSerializer(),
    responses={200: RspGetNoticeLogViewSerializer()},
)
