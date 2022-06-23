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

from django.db import models

from common.utils.local import local


def to_format_date(datetime, format="%Y-%m-%d %H:%M:%S"):
    """
    日期格式化
    """
    return datetime.strftime(format)


def to_date_time(string, format="%Y-%m-%d %H:%M:%S"):
    """
    日期转换
    """
    return datetime.strptime(string, format)


class FormatDateTimeField(models.DateTimeField):
    """
    格式化日期字段
    """

    def from_db_value(self, value, *args):
        return to_format_date(value) if value and isinstance(value, datetime) else ""

    def get_prep_value(self, value):
        if value:
            value = to_date_time(value) if isinstance(value, str) else value

        else:
            value = None

        return super().get_prep_value(value)


class BaseModel(models.Model):
    DISPLAY_FIELDS = (
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
        "description",
    )

    created_by = models.CharField("创建人", default="admin", max_length=255, null=True, blank=True)
    created_at = FormatDateTimeField("创建时间", auto_now_add=True, null=True, blank=True)
    updated_by = models.CharField("更新人", default="admin", max_length=255, null=True, blank=True)
    updated_at = FormatDateTimeField("更新时间", auto_now=True, null=True, blank=True)
    is_deleted = models.BooleanField("是否删除", default=False)
    deleted_by = models.CharField("删除人", default="admin", max_length=255, null=True, blank=True)
    deleted_at = FormatDateTimeField("删除时间", null=True, blank=True)
    description = models.TextField("描述", null=True, blank=True)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.created_by = local.request_username

        self.updated_by = local.request_username if local.request_username else self.updated_by
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
