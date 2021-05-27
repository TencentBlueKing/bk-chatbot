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
from rest_framework.fields import JSONField

from common.constants import CHAT_BOT_TYPES
from common.constants import TASK_PLATFORM_CHOICES
from module_intent.models import Bot
from module_intent.models import ExecutionLog
from module_intent.models import Intent
from module_intent.models import Task
from module_intent.models import Utterances


class BotSerializer(serializers.ModelSerializer):
    biz_id = serializers.IntegerField(required=True, label=_("业务ID"))
    biz_name = serializers.CharField(required=True, label=_("业务名称"))
    bot_id = serializers.CharField(required=True, label=_("业务名称"))
    bot_name = serializers.CharField(required=True, label=_("业务名称"))
    bot_type = serializers.ChoiceField(
        required=True,
        label=_("业务名称"),
        choices=CHAT_BOT_TYPES,
    )

    class Meta:
        model = Bot
        fields = (
            "id",
            "biz_id",
            "biz_name",
            "bot_id",
            "bot_name",
            "bot_type",
            "created_by",
            "created_at",
            "updated_at",
        )


class IntentSerializer(serializers.ModelSerializer):
    biz_id = serializers.IntegerField(required=True, label=_("业务ID"))
    index_id = serializers.IntegerField(required=True, label=_("索引ID"))
    intent_name = serializers.CharField(required=True, label=_("技能名称"))
    status = serializers.BooleanField(required=True, label=_("意图状态"))
    available_user = JSONField(required=True, label=_("可执行用户"))
    available_group = JSONField(required=True, label=_("可执行群组"))
    is_commit = serializers.BooleanField(required=True, label=_("执行确认"))

    class Meta:
        model = Intent
        fields = "__all__"


class UtterancesSerializer(serializers.ModelSerializer):
    biz_id = serializers.IntegerField(required=True, label=_("业务ID"))
    index_id = serializers.IntegerField(required=True, label=_("索引ID"))
    content = JSONField(required=True, label=_("语料列表"))

    class Meta:
        model = Utterances
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    biz_id = serializers.IntegerField(required=True, label=_("业务ID"))
    index_id = serializers.IntegerField(required=True, label=_("索引ID"))
    platform = serializers.ChoiceField(
        required=True,
        label=_("平台名称"),
        choices=TASK_PLATFORM_CHOICES,
    )
    task_id = serializers.CharField(required=True, label=_("任务ID"))
    activities = JSONField(required=True, label=_("节点信息"))
    slots = JSONField(required=True, label=_("槽位信息"))
    source = JSONField(required=True, label=_("任务元数据"))
    script = JSONField(required=True, label=_("执行脚本信息"))

    class Meta:
        model = Task
        fields = "__all__"


class ExecutionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutionLog
        fields = "__all__"
