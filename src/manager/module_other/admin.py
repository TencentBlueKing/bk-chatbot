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

from src.manager.module_other.models import (
    FAQModel,
    IMTypeModel,
    PluginTagModel,
    VersionModel,
)


@admin.register(VersionModel)
class VersionModelAdmin(admin.ModelAdmin):
    fields = ["is_show", "version", "title", "context_type", "context", "author"]
    list_display = ["is_show", "version", "title", "context", "author", "updated_at"]
    list_filter = ["is_show", "version", "title", "context", "author", "updated_at"]
    search_fields = ["is_show", "version", "title", "context", "author", "updated_at"]


@admin.register(PluginTagModel)
class PluginTagModelAdmin(admin.ModelAdmin):
    fields = ["key", "name"]
    list_display = ["key", "name", "created_by", "updated_at"]
    list_filter = ["key", "name", "created_by", "updated_at"]
    search_fields = ["key", "name", "created_by", "updated_at"]


@admin.register(FAQModel)
class FAQAdmin(admin.ModelAdmin):
    fields = ["faq_name", "faq_db", "faq_collection", "created_by"]
    list_display = ["faq_name", "faq_db", "faq_collection", "created_by", "updated_at"]
    list_filter = ["faq_name", "faq_db", "faq_collection", "created_by", "updated_at"]
    search_fields = ["faq_name", "faq_db", "faq_collection", "created_by", "updated_at"]


@admin.register(IMTypeModel)
class IMTypeAdmin(admin.ModelAdmin):
    fields = ["platform", "im_type_id", "im_type", "alias", "define"]
    list_display = ["platform", "im_type_id", "im_type", "alias", "created_by", "updated_at"]
    list_filter = ["platform", "im_type_id", "im_type", "alias", "created_by", "updated_at"]
    search_fields = ["platform", "im_type_id", "im_type", "alias", "created_by", "updated_at"]
