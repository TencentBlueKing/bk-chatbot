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
from django.utils.translation import ugettext_lazy as _
from django_filters import filters

from common.constants import CHAT_BOT_TYPE_WEWORK, CHAT_BOT_TYPES
from common.drf.filters import BaseOpenApiFilter
from common.models.base import BaseModel


class ChatBindBusiness(BaseModel):
    """
    沟通群所属的业务
    绑定规则：
        一个业务支持绑定多个群
        一个群不支持绑定多个业务
    """

    chat_index_id = models.CharField(
        _("群聊ID索引"),
        default="-1",
        max_length=255,
    )
    chat_group_id = models.CharField(
        _("群聊ID"),
        default="-1",
        max_length=255,
        primary_key=True,
    )
    chat_group_name = models.CharField(
        _("群聊名称"),
        default="-",
        max_length=255,
    )
    chat_bot_type = models.CharField(
        _("机器人类型"),
        default=CHAT_BOT_TYPE_WEWORK,
        max_length=50,
        choices=CHAT_BOT_TYPES,
    )
    biz_id = models.PositiveIntegerField(_("业务ID"), default=0)
    biz_name = models.CharField(_("业务名称"), default="", max_length=255)

    @property
    def chat_id(self):
        return self.chat_group_id

    class Meta:
        db_table = "tab_chat_bind_business"
        verbose_name = _("群ID绑定业务表")
        verbose_name_plural = _("群ID绑定业务表")

    class OpenApiFilter(BaseOpenApiFilter):
        """
        提供给rest查询使用
        """

        biz_id = filters.NumberFilter(field_name="biz_id")
        chat_index_id = filters.CharFilter(field_name="chat_index_id")
        chat_group_id = filters.CharFilter(field_name="chat_group_id")
        is_deleted = filters.BooleanFilter(field_name="is_deleted")
