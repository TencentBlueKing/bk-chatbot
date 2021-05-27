# -*- coding: utf-8 -*-
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
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from common.constants import CHAT_BOT_TYPE_WEWORK
from common.constants import CHAT_BOT_TYPES
from common.utils.local import local


class BaseModel(models.Model):
    DISPLAY_FIELDS = (
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
        "description",
    )

    created_by = models.CharField("创建人", max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(
        "创建时间",
        auto_now_add=True,
        null=True,
        blank=True,
    )
    updated_by = models.CharField("更新人", max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField("更新时间", null=True, blank=True)
    is_deleted = models.BooleanField("是否删除", default=False)
    deleted_by = models.CharField("删除人", max_length=255, null=True, blank=True)
    deleted_at = models.DateTimeField("删除时间", null=True, blank=True)
    description = models.TextField("描述", null=True, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.created_at = timezone.now()
            self.created_by = local.request_username

        self.updated_at = timezone.now()
        self.updated_by = local.request_username
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


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
        verbose_name = _("群ID绑定业务表")
        verbose_name_plural = _("群ID绑定业务表")
