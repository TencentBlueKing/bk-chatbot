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

from common.drf.filters import BaseOpenApiFilter
from common.models.base import BaseModel
from common.models.json import DictCharField


class VersionModel(BaseModel):
    """
    版本
    """

    is_show = models.BooleanField("是否展示")
    version = models.CharField("版本", unique=True, max_length=255)
    title = models.CharField("主题", max_length=255)
    context = DictCharField("内容", help_text="输入一个字符串数组")
    author = models.CharField("发版人", max_length=128)

    class Meta:
        db_table = "tab_version"
        verbose_name = "【版本】"
        verbose_name_plural = "【版本】"

    class OpenApiFilter(BaseOpenApiFilter):
        """
        过滤
        """

        is_show = filters.BooleanFilter(field_name="is_show")
        version = filters.CharFilter(field_name="version", lookup_expr="contains")
        title = filters.CharFilter(field_name="title", lookup_expr="contains")
        author = filters.CharFilter(field_name="author", lookup_expr="contains")


class PluginTagModel(BaseModel):
    """
    插件标签
    """

    key = models.CharField("插件标签唯一key", unique=True, max_length=64, null=False)
    name = models.CharField("插件标签唯一名称", unique=True, max_length=128, null=False)

    class Meta:
        db_table = "tab_plugin_tag"
        verbose_name = "【插件标签】"
        verbose_name_plural = "【插件标签】"

    class OpenApiFilter(BaseOpenApiFilter):
        """
        过滤
        """

        key = filters.BooleanFilter(field_name="key", lookup_expr="contains")
        name = filters.CharFilter(field_name="name", lookup_expr="contains")


class FAQModel(BaseModel):
    """
    知识库
    """

    biz_id = models.PositiveIntegerField(_("业务ID"), default=0)
    biz_name = models.CharField(_("业务名称"), default="", max_length=128)
    faq_name = models.CharField(_("知识库名称"), default="", max_length=128)
    faq_db = models.CharField(_("知识库DB"), default="", max_length=128)
    faq_collection = models.CharField(_("知识库表名"), default="", max_length=128)
    num = models.CharField(_("QA数量"), default="", max_length=128)
    member = models.TextField(_("维护人员"), default="")

    class Meta:
        db_table = "tab_faq"
        verbose_name = _("【知识库】")
        verbose_name_plural = _("【知识库】")

    @classmethod
    def create_faq(cls, **kwargs):
        """
        创建知识库
        """
        return cls.objects.get_or_create(**kwargs)

    @classmethod
    def query_faq_list(cls, **kwargs):
        """
        获取知识库
        """
        return list(cls.objects.filter(**kwargs).values())

    @classmethod
    def update_faq(cls, faq_id, **kwargs):
        """
        更新知识库
        """
        cls.objects.filter(pk=faq_id).update(**kwargs)

    class OpenApiFilter(BaseOpenApiFilter):
        """
        过滤
        """

        biz_id = filters.BooleanFilter(field_name="biz_id", lookup_expr="exact")
        faq_name = filters.CharFilter(field_name="faq_name", lookup_expr="exact")
        faq_db = filters.CharFilter(field_name="faq_db", lookup_expr="exact")
        num = filters.CharFilter(field_name="num", lookup_expr="exact")
        member = filters.CharFilter(field_name="member", lookup_expr="contains")
        created_by = filters.CharFilter(field_name="created_by", lookup_expr="exact")