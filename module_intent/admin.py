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
from django.contrib import admin

from module_intent.models import Bot
from module_intent.models import ExecutionLog
from module_intent.models import Intent
from module_intent.models import Task
from module_intent.models import Utterances


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = [
        "biz_id",
        "biz_name",
        "bot_id",
        "bot_name",
        "bot_type",
        "created_by",
        "created_at",
        "is_deleted",
    ]
    list_filter = [
        "biz_id",
        "biz_name",
        "bot_id",
        "bot_name",
        "bot_type",
        "created_by",
        "created_at",
        "is_deleted",
    ]
    search_fields = [
        "biz_name",
        "biz_id",
        "bot_name",
        "bot_id",
        "bot_type",
        "created_by",
    ]


@admin.register(Intent)
class IntentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "index_id",
        "biz_id",
        "intent_name",
        "status",
        "created_by",
        "created_at",
        "is_deleted",
    ]
    list_filter = [
        "id",
        "index_id",
        "biz_id",
        "intent_name",
        "status",
        "created_by",
        "created_at",
        "is_deleted",
    ]
    search_fields = ["intent_name", "biz_id", "index_id", "created_by"]


@admin.register(Utterances)
class UtterancesAdmin(admin.ModelAdmin):
    list_display = ["id", "index_id", "biz_id"]
    list_filter = ["id", "index_id", "biz_id"]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        "index_id",
        "biz_id",
        "platform",
        "task_id",
    ]
    list_filter = [
        "index_id",
        "biz_id",
        "platform",
        "task_id",
    ]
    search_fields = ["index_id", "biz_id", "platform", "task_id"]


@admin.register(ExecutionLog)
class ExecutionLogAdmin(admin.ModelAdmin):
    list_display = [
        "biz_id",
        "bot_type",
        "bot_name",
        "intent_id",
        "intent_name",
        "platform",
        "task_id",
        "sender",
        "msg",
        "status",
        "start_time",
        "end_time",
    ]
    list_filter = [
        "biz_id",
        "bot_type",
        "bot_name",
        "intent_id",
        "intent_name",
        "platform",
        "task_id",
        "sender",
        "msg",
        "status",
        "start_time",
        "end_time",
    ]
    search_fields = [
        "biz_id",
        "bot_type",
        "bot_name",
        "intent_id",
        "intent_name",
        "platform",
        "task_id",
        "sender",
        "msg",
        "status",
        "start_time",
        "end_time",
    ]
