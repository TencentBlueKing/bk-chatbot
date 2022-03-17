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


class Plugin(BaseModel):
    """
    插件
    """

    class PluginStatus(Enum):
        """
        插件状态
        """

        DEFAULT = 0  # 默认状态
        STAG = 1  # 预发布
        AUDIT = 2  # 审核状态
        ADDED = 3  # 上架状态
        SOLD_OUT = 4  # 下架
        CANCEL_AUDIT = 5  # 取消审核

    class PluginType(Enum):
        """
        插件类型
        """

        PRIVATE = 0  # 私有插件
        PUBLIC = 1  # 公有插件

    plugin_key = models.CharField("插件key", max_length=128, unique=True)
    plugin_icon = models.CharField("插件图标", max_length=512)
    plugin_name = models.CharField("插件名称", max_length=128, unique=True)
    plugin_addr = models.CharField("插件地址", max_length=256)
    plugin_desc = models.CharField("插件描叙", max_length=512)
    plugin_tag = models.CharField("插件标签", max_length=128)
    plugin_status = models.IntegerField(
        "插件状态",
        default=PluginStatus.DEFAULT.value,
        choices=((tag.value, tag.name) for tag in PluginStatus),
    )
    plugin_type = models.IntegerField(
        "插件类型",
        default=PluginType.PRIVATE.value,
        choices=((tag.value, tag.name) for tag in PluginType),
    )
    biz_list = DictCharField(verbose_name="生效业务", default=[])
    choose_biz = models.BooleanField("选择业务", default=False)
    developers = DictCharField("开发者", default=[])
    actions = DictCharField("插件动作", default=[])
    plugin_global = DictCharField("全局变量", default={})
    plugin_exec_count = models.IntegerField("执行总次数", default=0)
    plugin_lately_count = models.IntegerField("插件最近30天执行次数", default=0)

    class Meta:
        db_table = "tab_plugins"

    class OpenApiFilter(BaseOpenApiFilter):
        """
        提供给rest查询使用
        """

        plugin_name = filters.CharFilter(field_name="plugin_name", lookup_expr="contains")
        developers = filters.CharFilter(field_name="developers", lookup_expr="contains")
        plugin_status = filters.CharFilter(field_name="plugin_status", lookup_expr="exact")
        plugin_type = filters.CharFilter(field_name="plugin_type", method="self_or")
        biz_list = filters.CharFilter(field_name="biz_list", method="self_or", lookup_expr="contains")
        biz_id = filters.CharFilter(field_name="biz_list", method="self_ignore")
        plugin_lately_count = filters.CharFilter(field_name="plugin_lately_count", lookup_expr="gt")


class PluginAuditLog(BaseModel):
    """
    插件审核日志
    """

    class SnStatus(Enum):
        DEFAULT = 0  # 默认状态
        PASS = 1  # 通过
        NO_PASS = 2  # 不通过

    sn = models.CharField("单据号", max_length=255, unique=True)
    sn_status = models.IntegerField(
        "单据审核状态",
        default=SnStatus.DEFAULT.value,
        choices=((tag.value, tag.name) for tag in SnStatus),
    )
    plugin_id = models.IntegerField("插件单据")
    plugin_username = models.CharField("添加人", max_length=255)

    class Meta:
        db_table = "tab_plugin_audit_log"

    @classmethod
    def update_log(cls, sn, **kwargs):
        """
        更新意图
        """
        cls.objects.filter(sn=sn).update(**kwargs)
