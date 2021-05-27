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

from common.constants import CHAT_BOT_TYPES
from module_biz.models import ChatBindBusiness


class GroupBindBizSerializer(serializers.ModelSerializer):
    chat_group_id = serializers.CharField(required=True, label=_("群聊ID"))
    chat_group_name = serializers.CharField(required=True, label=_("群聊名称"))
    chat_bot_type = serializers.ChoiceField(
        required=True,
        label=_("机器人类型"),
        choices=CHAT_BOT_TYPES,
    )
    biz_id = serializers.CharField(required=True, label=_("业务ID"))
    biz_name = serializers.CharField(required=True, label=_("业务名称"))

    class Meta:
        model = ChatBindBusiness
        fields = "__all__"


class SummaryGroupBindBizSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatBindBusiness
        fields = ("chat_index_id", "chat_group_name",)
