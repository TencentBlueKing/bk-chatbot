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

from datetime import datetime

from croniter import croniter
from dateutil.parser import parse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.serializers import Serializer

from common.drf.field import TimeStampSerializer
from module_timer.models import TimerModel
from module_timer.proto import timer_tag


class TimerSerializer(serializers.ModelSerializer):
    """
    timer序列化器
    """

    execute_time = TimeStampSerializer(label="定时执行时间", allow_null=True, allow_blank=True)
    expression = serializers.CharField(label="cron定义", allow_null=True, allow_blank=True)
    exec_data = serializers.DictField(label="请求数据")

    def validate(self, value):
        """
        认证
        @param value:
        @return:
        """

        execute_time = value.get("execute_time")
        expression = value.get("expression")
        if execute_time == "" and expression == "":
            raise ValueError("[定时任务表达是]和[计划执行时间]不能都为空")
        if execute_time != "" and expression != "":
            raise ValueError("[定时任务表达是]和[计划执行时间]不能都存在")
        return value

    def validate_expression(self, value):
        """
        验证crontab是否正确
        @param value:
        @return:
        """
        # 为空直接不处理
        if value == "":
            return value

        ok = croniter.is_valid(value)
        if not ok:
            raise ValueError(f"定时任务表达【{value}】表达式输入错误")
        return value

    def validate_execute_time(self, value):
        """
        处理时间
        @param value:
        @return:
        """
        # 为空直接不处理
        if value == "":
            return value
        execute_time = int(datetime.timestamp(parse(value, ignoretz=True)))
        now_time = int(datetime.timestamp(datetime.now()))
        # 预留1分钟的buff
        if now_time + 60 >= execute_time:
            raise ValueError(f"定时任务执行时间【{value}】已失效")
        return str(execute_time)

    class Meta:
        model = TimerModel
        fields = [
            "id",
            "biz_id",
            "timer_name",
            "exec_data",
            "execute_time",
            "expression",
            "timer_status",
            "timer_user",
        ]


class ReqPutTimerSerializer(serializers.ModelSerializer):
    """
    修改数据请求数据
    """

    class Meta:
        model = TimerModel
        fields = ["timer_status"]


class ReqCallbackTimerSerializer(Serializer):
    """
    修改数据请求数据
    """

    id = serializers.IntegerField(label="调用id")


############################################################

timer_list_docs = swagger_auto_schema(
    tags=timer_tag,
    operation_id="定时任务管理-查询",
)

timer_create_docs = swagger_auto_schema(
    tags=timer_tag,
    operation_id="定时任务管理-添加",
)

timer_update_docs = swagger_auto_schema(
    tags=timer_tag,
    operation_id="定时任务管理-修改",
)
timer_del_docs = swagger_auto_schema(
    tags=timer_tag,
    operation_id="定时任务管理-删除",
)

timer_callback_docs = swagger_auto_schema(
    tags=timer_tag,
    request_body=ReqCallbackTimerSerializer(),
    operation_id="定时任务管理-回调接口",
)
