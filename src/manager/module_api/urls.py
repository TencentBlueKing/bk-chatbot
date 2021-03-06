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

from src.manager.module_api.views import (
    admin_views,
    biz_variable_views,
    bkmonitor_views,
    cmdb_views,
    intent_view,
)

router = routers.DefaultRouter()

# 路由注册
router.register(r"bkmonitor", bkmonitor_views.BkMonitorViewSet, basename="bkmonitor")
router.register(r"cmdb", cmdb_views.CmdbViewSet, basename="cmdb")
router.register(r"admin/intent", intent_view.IntentViewSet, basename="intent_api")
router.register(r"biz/variable", biz_variable_views.BizVariableViewSet, basename="biz_variable_api")

urlpatterns = (
    url(r"^exec/admin_describe_intents", admin_views.admin_describe_intents),
    url(r"^exec/admin_describe_tasks", admin_views.admin_describe_tasks),
    url(r"^exec/admin_describe_utterances", admin_views.admin_describe_utterances),
    url(r"^", include(router.urls)),
)
