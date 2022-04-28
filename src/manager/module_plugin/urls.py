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


from django.conf.urls import include, url
from rest_framework import routers


from src.manager.module_plugin.views.plugin_view import PluginViewSet
from src.manager.module_plugin.views.audit_view import PluginAuditViewSet

router = routers.DefaultRouter()

router.register(r"plugin", PluginViewSet, basename="manage_plugin")  # 插件管理
router.register(r"plugin/audit", PluginAuditViewSet, basename="plugin_audit")  # 插件审核

urlpatterns = (url(r"^manage/", include(router.urls)),)
