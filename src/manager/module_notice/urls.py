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

from src.manager.module_notice.views.alarm_view import AlarmConfigViewSet, AlarmViewSet
from src.manager.module_notice.views.notice_view import NoticeGroupViewSet
from src.manager.module_notice.views.trigger_view import TriggerViewSet
from src.manager.module_notice.views.whitelist_view import WhiteListViewSet

router = routers.DefaultRouter()

router.register(r"trigger", TriggerViewSet, basename="trigger")  # 触发器
router.register(r"notice_group", NoticeGroupViewSet, basename="notice")  # 通知群组
router.register(r"whitelist", WhiteListViewSet, basename="whitelist")  # 白名单
router.register(r"alarm", AlarmViewSet, basename="alarm")  # 告警
router.register(r"config/alarm", AlarmConfigViewSet, basename="alarm_config")  # 告警

urlpatterns = (url(r"^", include(router.urls)),)
