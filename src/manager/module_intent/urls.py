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

from src.manager.module_intent.views.bot_views import BotViewSet
from src.manager.module_intent.views.intent_views import IntentViewSet
from src.manager.module_intent.views.exec_views import TaskExecutionViewSet, ExecutionLogViewSet
from src.manager.module_intent.views.tasks_views import TasksViewSet
from src.manager.module_intent.views.utterance_views import UtterancesViewSet

router = routers.DefaultRouter()

router.register(r"(?P<biz>\d+)/bot", BotViewSet)
router.register(r"(?P<biz>\d+)/intent", IntentViewSet)
router.register(r"(?P<biz>\d+)/utterance", UtterancesViewSet)
router.register(r"(?P<biz>\d+)/tasks", TasksViewSet)
router.register(r"log", ExecutionLogViewSet)
router.register(r"task/exec", TaskExecutionViewSet, basename="task_exec")

urlpatterns = (url(r"^", include(router.urls)),)
