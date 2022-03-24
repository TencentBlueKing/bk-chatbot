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
from django.contrib import admin
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="BK-CHAT API",
        default_version="v1",
        description="this is bkchat api",
    ),
    public=True,
)
urlpatterns = [
    # 出于安全考虑，默认屏蔽admin访问路径。
    # 开启前请修改路径随机内容，降低被猜测命中几率，提升安全性
    # 系统代码
    url(r"^admin_opsbot/", admin.site.urls),
    url(r"^account/", include("blueapps.account.urls")),
    url(r"^i18n/", include("django.conf.urls.i18n")),
    url(r"^", include("src.manager.module_index.urls")),
    # 业务逻辑
    url(r"^api/v1/", include("src.manager.module_api.urls")),
    url(r"^api/v1/", include("src.manager.module_biz.urls")),
    url(r"^api/v1/", include("src.manager.module_intent.urls")),
    url(r"^api/v1/", include("src.manager.module_faq.urls")),
    url(r"^api/v1/", include("src.manager.module_nlp.urls")),
    url(r"^api/v1/", include("src.manager.module_plugin.urls")),
    url(r"^api/v1/", include("src.manager.module_timer.urls")),
    url(r"^api/v1/", include("src.manager.module_other.urls")),
    # 文档
    url(r"^swagger/$", schema_view.with_ui("swagger"), name="schema-swagger-ui"),
    url(r"^api-docs/$", schema_view.with_ui("redoc"), name="schema-docs"),
]
