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

from src.manager.module_biz.models import ChatBindBusiness


class ChatBindBusinessAdmin(admin.ModelAdmin):
    list_display = ("chat_group_id", "chat_bot_type", "biz_id", "biz_name")
    list_filter = ("chat_group_id", "chat_bot_type", "biz_id", "biz_name")
    search_fields = ("chat_group_id", "chat_bot_type", "biz_id", "biz_name")


admin.site.register(ChatBindBusiness, ChatBindBusinessAdmin)
