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
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from module_faq.models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    biz_id = serializers.IntegerField(required=True, label=_("业务ID"))
    biz_name = serializers.CharField(required=True, label=_("业务名称"))
    faq_name = serializers.CharField(required=True, label=_("知识库名称"))
    faq_db = serializers.CharField(required=True, label=_("知识库DB"))
    faq_collection = serializers.CharField(required=True, label=_("知识库表名"))
    num = serializers.CharField(required=True, label=_("QA数量"))
    member = serializers.CharField(required=True, label=_("维护人员"))

    class Meta:
        model = FAQ
        fields = "__all__"
