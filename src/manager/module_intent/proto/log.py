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
from src.manager.module_intent.handler import TaskType
from src.manager.module_intent.models import ExecutionLog


class ExecutionLogSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    params = serializers.ListField(label="请求参数")

    class Meta:
        model = ExecutionLog
        fields = [
            "id",
            "intent_id",
            "intent_name",
            "sender",
            "status",
            "platform",
            "params",
            "created_at",
            "project_id",
            "feature_id",
            "task_id",
            "biz_id",
        ]


class RspListExecutionLog(BaseRspSerializer):
    pass


class ReqBotCreateLogData(Serializer):
    class ReqBotCreateLogDataParam(Serializer):
        """
        请求参数
        """

        id = serializers.CharField(label="参数id")
        name = serializers.CharField(label="参数名称")
        value = serializers.CharField(label="参数值")

    biz_id = serializers.IntegerField(label="业务ID")
    bot_type = serializers.CharField(label="机器人类型")
    bot_name = serializers.CharField(label="机器人名称")
    intent_id = serializers.CharField(label="意图ID")
    intent_name = serializers.CharField(label="技能名称")
    intent_create_user = serializers.CharField(label="意图添加人")
    platform = serializers.IntegerField(min_value=0, max_value=len(list(ExecutionLog.PlatformType)), label="机器人名称")
    project_id = serializers.CharField(required=False, allow_blank=True, label="项目ID")
    feature_id = serializers.CharField(required=False, allow_blank=True, label="特色ID")
    task_id = serializers.CharField(required=True, label="任务ID")
    sender = serializers.CharField(required=True, label="机器人名称")
    msg = serializers.CharField(required=True, label="机器人名称")
    rtx = serializers.CharField(required=True, allow_blank=True, label="机器人名称")
    params = serializers.ListField(
        required=False,
        child=ReqBotCreateLogDataParam(),
        default=[],
        allow_null=True,
        label="请求参数",
    )


class ReqPostBotCreateLog(Serializer):
    """
    流水线列表
    """

    bk_app_code = serializers.CharField(required=False, label="bk_app_code")
    bk_app_secret = serializers.CharField(required=False, label="bk_app_secret")
    data = ReqBotCreateLogData()


class ResGetTaskInfo(Serializer):
    id = serializers.IntegerField(label="唯一id")


class RspGetTaskInfoData(Serializer):
    class RspGetTaskInfoData(Serializer):
        bk_biz_id = serializers.CharField(label="项目id", default="", required=False)
        project_id = serializers.CharField(label="蓝盾项目id", default="", required=False)
        pipeline_id = serializers.CharField(label="蓝盾流程id", default="", required=False)
        task_id = serializers.CharField(label="任务id", default="", required=False)
        node_id = serializers.CharField(label="节点id", default="", required=False)
        node_name = serializers.CharField(label="节点名称", default="", required=False)
        ip = serializers.CharField(label="IP", default="", required=False)
        error_msg = serializers.CharField(label="错误信息", default="", required=False)

    data = serializers.ListField(child=RspGetTaskInfoData())


class RspGetTaskInfo(BaseRspSerializer, RspGetTaskInfoData):
    """
    返回数据
    """

    pass


class RspGetTaskPipeline(BaseRspSerializer):
    """
    返回数据
    """

    data = serializers.DictField()


class ReqPostTaskOperate(Serializer):
    """
    操作请求数据
    """

    class ReqPostTaskOperateData(Serializer):
        node_id = serializers.CharField(label="标准任务单node操作", required=False)
        task_id = serializers.CharField(label="蓝盾单task_id操作", required=False)

    id = serializers.IntegerField(label="任务id")
    action = serializers.ChoiceField(
        label="操作类型",
        choices=[tag.value for tag in TaskType],
    )
    data = ReqPostTaskOperateData(required=False)


############################################################

log_tag = ["意图执行日志"]

log_list_docs = swagger_auto_schema(
    tags=log_tag,
    operation_id="执行日志-查询",
)
log_describe_records_docs = swagger_auto_schema(
    tags=log_tag,
    operation_id="JOB日志-查询",
)

exec_log_list_apigw_docs = swagger_auto_schema(
    tags=log_tag,
    operation_id="执行日志apigw-查询",
    responses={200: RspListExecutionLog()},
)
exec_log_create_apigw_docs = swagger_auto_schema(
    tags=log_tag,
    request_body=ReqPostBotCreateLog(),
    operation_id="执行日志apigw-添加",
    responses={200: RspListExecutionLog()},
)
exec_task_info_apigw_docs = swagger_auto_schema(
    tags=log_tag,
    operation_id="执行日志apigw-查看详情",
    responses={200: RspGetTaskInfo()},
)
exec_task_pipeline_apigw_docs = swagger_auto_schema(
    tags=log_tag,
    operation_id="执行日志apigw-pipeline",
    responses={200: RspGetTaskPipeline()},
)

exec_task_operate_apigw_docs = swagger_auto_schema(
    tags=log_tag,
    request_body=ReqPostTaskOperate(),
    operation_id="执行任务-停止",
    responses={200: RspGetTaskPipeline()},
)
