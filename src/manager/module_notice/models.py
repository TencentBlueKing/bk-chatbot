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

from enum import Enum

from django.db import models
from django_filters import filters

from common.drf.filters import BaseOpenApiFilter
from common.models.base import BaseModel, FormatDateTimeField
from common.models.json import DictCharField
from common.constants import TASK_PLATFORM_CHOICES


class TriggerModel(BaseModel):
    """
    触发器
    """

    biz_id = models.CharField("业务ID", default="system", max_length=256)
    name = models.CharField("名称", default="", max_length=256)
    trigger_key = models.CharField("触发器key", max_length=64, unique=True, default="")
    im_platform = models.CharField("平台", max_length=256)
    im_type = models.CharField("im类型", max_length=256)
    im_type_id = models.CharField("IM类型id", max_length=56, default="")
    info = DictCharField("触发器信息", default=[])

    class Meta:
        db_table = "tab_trigger"
        verbose_name = "【触发器】"
        verbose_name_plural = "【触发器】"

    class OpenApiFilter(BaseOpenApiFilter):
        """
        提供给rest查询使用
        """

        biz_id = filters.CharFilter(field_name="biz_id")
        name = filters.CharFilter(field_name="name")
        im_platform = filters.CharFilter(field_name="im_platform")
        im_type = filters.CharFilter(field_name="im_type")
        trigger_key = filters.CharFilter(field_name="trigger_key")


class NoticeGroupModel(BaseModel):
    """
    通知群组
    """

    class NoticeType(Enum):
        """
        通知类型
        """

        SINGLE = 1
        GROUP = 2

    biz_id = models.CharField("业务ID", max_length=256)
    name = models.CharField("名称", default="", max_length=256)
    trigger_id = models.IntegerField("触发器id")
    trigger_name = models.CharField("触发器名称", max_length=256)
    group_type = models.CharField("类型", max_length=64)
    group_value = DictCharField("通知类型的值")

    class Meta:
        db_table = "tab_notice_group"
        verbose_name = "【通知群组】"
        verbose_name_plural = "【通知群组】"

    class OpenApiFilter(BaseOpenApiFilter):
        """
        提供给rest查询使用
        """

        biz_id = filters.CharFilter(field_name="biz_id")
        name = filters.CharFilter(field_name="name")
        trigger_name = filters.CharFilter(field_name="trigger_name")
        group_value = filters.CharFilter(field_name="group_value", lookup_expr="icontains")
        created_by = filters.CharFilter(field_name="created_by")


class WhitelistModel(BaseModel):
    """
    白名单
    """

    biz_id = models.CharField("业务ID", max_length=256)
    whitelist_ip = models.CharField("外网IP", max_length=32)

    class Meta:
        db_table = "tab_whitelist"
        verbose_name = "【业务白名单】"
        verbose_name_plural = "【业务白名单】"

    class OpenApiFilter(BaseOpenApiFilter):
        """
        提供给rest查询使用
        """

        biz_id = filters.CharFilter(field_name="biz_id")
        white_ip = filters.CharFilter(field_name="white_ip")
        created_by = filters.CharFilter(field_name="created_by")


class AlarmStrategyModel(BaseModel):
    """
    告警策略
    """

    class AlarmSourceType(Enum):
        """
        告警源
        """

        BKM = 1  # 蓝鲸监控
        BCS = 2

    class DealStrategyType(Enum):
        """
        处理策略类型
        """

        NOTICE = 1  # 通知类
        EVENT = 2  # 事件类

    deal_alarm_name = models.CharField("处理套餐名称", max_length=256)
    biz_id = models.CharField("业务ID", max_length=256)
    alarm_source_type = models.IntegerField(
        "告警源",
        choices=[(tag.value, tag.name) for tag in AlarmSourceType],
    )
    alarm_strategy = DictCharField("告警策略")
    deal_strategy_type = models.IntegerField(
        "处理策略类型",
        choices=[(tag.value, tag.name) for tag in DealStrategyType],
    )
    deal_strategy_value = DictCharField("处理策略值")
    is_enabled = models.BooleanField("是否启动", default=False)
    config_id = models.CharField("处理套餐ID", max_length=256)
    is_translated = models.BooleanField("是否翻译", default=False)
    translation_type = models.CharField("目标语言", max_length=32, default="", blank=True)

    class Meta:
        db_table = "tab_alarm_strategy"
        verbose_name = "【告警策略】"
        verbose_name_plural = "【告警策略】"
        unique_together = ("biz_id", "deal_alarm_name")

    class OpenApiFilter(BaseOpenApiFilter):
        """
        提供给rest查询使用
        """

        biz_id = filters.CharFilter(field_name="biz_id")
        alarm_source_type = filters.CharFilter(field_name="alarm_source_type")
        created_by = filters.CharFilter(field_name="created_by")


class TaskBroadcast(models.Model):
    biz_id = models.CharField("业务ID", max_length=256)
    task_id = models.CharField("任务ID", max_length=256)
    platform = models.CharField("任务所属平台", choices=TASK_PLATFORM_CHOICES, max_length=32)
    session_id = models.CharField("触发实时播报的会话ID", max_length=256)

    start_user = models.CharField("开始播报人", max_length=256)
    stop_user = models.CharField("终止播报人", max_length=256, null=True, blank=True)
    start_time = FormatDateTimeField("开始播报时间", auto_now_add=True, null=True, blank=True)
    stop_time = FormatDateTimeField("终止播报时间", null=True, blank=True)
    next_broadcast_time = FormatDateTimeField("阶梯播报下一次播报时间", null=True, blank=True)
    broadcast_num = models.IntegerField("同一节点播报次数", default=0)

    step_id = models.CharField("任务当前步骤ID", max_length=256, null=True, blank=True)
    step_status = models.CharField("当前步骤状态", max_length=256, null=True, blank=True)
    is_stop = models.BooleanField("是否停止播报", default=False)
    share_group_list = DictCharField("分享播报用户组列表", default=[])

    class Meta:
        db_table = "tab_task_broadcast"
        verbose_name = "【任务播报】"
        verbose_name_plural = "【任务播报】"
