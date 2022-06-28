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
from common.models.base import BaseModel
from common.models.json import DictCharField


class TriggerModel(BaseModel):
    """
    触发器
    """

    biz_id = models.CharField("业务ID", default="system", max_length=256)
    name = models.CharField("名称", default="", max_length=256)
    trigger_key = models.CharField("触发器key", max_length=64, unique=True, default="")
    im_platform = models.CharField("平台", max_length=256, default=0)
    im_type = models.CharField("im类型", max_length=256, default=0)
    info = DictCharField("触发器信息", default="")

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
