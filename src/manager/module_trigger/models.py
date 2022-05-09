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

from django.db import models
from django_filters import filters

from common.drf.filters import BaseOpenApiFilter
from common.models.base import BaseModel
from common.models.json import DictCharField


class TriggerModel(BaseModel):
    """
    触发器
    """

    name = models.CharField("名称", default="", max_length=256)
    platform = models.CharField("平台", max_length=256, default=0)
    trigger_type = models.CharField("触发器类型", max_length=256, default=0)
    trigger_key = models.CharField("触发器key", max_length=256, default="")
    info = DictCharField("触发器信息", default="")

    class Meta:
        db_table = "tab_trigger"

    class OpenApiFilter(BaseOpenApiFilter):
        """
        提供给rest查询使用
        """

        name = filters.CharFilter(field_name="name")
        platform = filters.CharFilter(field_name="platform")
        trigger_type = filters.CharFilter(field_name="trigger_type")
        trigger_key = filters.CharFilter(field_name="trigger_key")
