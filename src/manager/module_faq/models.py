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

from common.models.base import BaseModel


class FAQ(BaseModel):
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
