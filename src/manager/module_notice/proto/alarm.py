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

from common.drf.field import BizId
from src.manager.module_notice.models import AlarmStrategyModel, NoticeGroupModel
from src.manager.module_notice.proto import notice_tag

# 需要处理的基础字段
BaseMetaFields = [
    "id",
    "deal_alarm_name",
    "alarm_source_type",
    "alarm_strategy",
    "deal_strategy_type",
    "deal_strategy_value",
    "is_enabled",
]


class ReqGetAlarmStrategySerializer(serializers.Serializer):
    """
    查询策略
    """

    platform = serializers.IntegerField(label="平台")


class ReqPostAlarmStrategySendMsgSerializer(serializers.Serializer):
    """
    查询策略
    """

    config_id = serializers.IntegerField(label="平台")


class AlarmConfigSerializer(serializers.ModelSerializer):
    """
    告警配置
    """

    class AlarmConfigSerializerAlarmStrategy(serializers.Serializer):
        """
        策略选择
        """

        id = serializers.CharField(label="唯一ID")
        name = serializers.CharField(label="策略名称")

    class AlarmConfigSerializerDealStrategyValue(serializers.Serializer):
        """
        策略值
        """

        url = serializers.CharField(label="http回调地址", required=False)
        notice_group_ids = serializers.ListSerializer(
            label="http回调地址", child=serializers.IntegerField(), required=False
        )

        def validate_notice_group_ids(self, value):
            """
            验证是否存在告警群组
            @param value:
            @return:
            """
            notice_groups = NoticeGroupModel.objects.filter(id__in=value).values("id")
            query_ids = list(map(lambda x: x.get("id"), notice_groups))
            diff_ids = list(set(value).difference(set(query_ids)))
            if len(diff_ids) > 0:
                raise ValueError(f"不存在的通知群组ID为:{diff_ids}")
            return value

    deal_strategy_value = AlarmConfigSerializerDealStrategyValue()
    alarm_strategy = serializers.ListField(
        label="告警策略列表",
        allow_empty=False,
        child=AlarmConfigSerializerAlarmStrategy(),
    )

    class Meta:
        model = AlarmStrategyModel
        fields = BaseMetaFields + ["biz_id", "created_by", "config_id"]


class ReqPostAlarmConfigSerializer(AlarmConfigSerializer):
    """
    添加
    """

    biz_id = serializers.HiddenField(default=BizId())
    created_by = serializers.HiddenField(default="")

    class Meta:
        model = AlarmStrategyModel
        fields = BaseMetaFields + ["biz_id", "created_by"]


class ReqPutAlarmConfigSerializer(AlarmConfigSerializer):
    """
    修改
    """

    class Meta:
        model = AlarmStrategyModel
        fields = BaseMetaFields


###############################
# 查询策略
alarm_strategy_list_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="群组-修改",
    query_serializer=ReqGetAlarmStrategySerializer(),
)
# 通知接口(api_gw)
alarm_strategy_notice_docs = swagger_auto_schema(
    tags=notice_tag,
    auto_schema=None,
    request_body=ReqPostAlarmStrategySendMsgSerializer(),
)

# 告警配置相关
alarm_config_list_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="告警配置-展示",
)
alarm_config_create_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="告警配置-添加",
)
alarm_config_update_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="告警配置-修改",
)
alarm_config_delete_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="告警配置-删除",
)
