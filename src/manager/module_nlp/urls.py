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

from src.manager.module_nlp.views.corpus_view import CorpusViewSet, DomainViewSet, IntentViewSet

router = routers.DefaultRouter()

router.register(r"domain", DomainViewSet, basename="corpus_domain")  # 领域
router.register(r"intent", IntentViewSet, basename="corpus_intent")  # 意图
router.register(r"manage", CorpusViewSet, basename="corpus")  # 语料


urlpatterns = (url(r"^corpus/", include(router.urls)),)
