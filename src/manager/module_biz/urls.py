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
from django.conf.urls import include, url
from rest_framework import routers

from src.manager.module_biz.views.biz_views import BizViewSet
from src.manager.module_biz.views.chat_bind_views import ChatBindViewSet, OpenChatBindViewSet
from src.manager.module_biz.views.summary_chat_bind import SummaryChatBindViewSet
from src.manager.module_biz.views.task_views import TaskViewSet

router = routers.DefaultRouter()

router.register(r"biz", BizViewSet, basename="biz")
router.register(r"task/(?P<biz_id>.*)", TaskViewSet, basename="task")
router.register(r"chat_bind", ChatBindViewSet, basename="chat_bind")
router.register(r"open_chat_bind", OpenChatBindViewSet, basename="open_chat_bind")

router.register(
    r"summary_chat_bind",
    SummaryChatBindViewSet,
    basename="summary_chat_bind",
)

urlpatterns = (url(r"^", include(router.urls)),)
