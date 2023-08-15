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

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views import static
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
import version_log.config as config

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
    # 版本日志
    url(rf"^{config.ENTRANCE_URL}", include("version_log.urls", namespace="version_log")),
    # 业务逻辑
    url(r"^", include("src.manager.urls")),  # 入口urls
    url(r"^static/(?P<path>.*)$", static.serve, {"document_root": settings.STATICFILES_DIRS[0]}, name="static"),
    # 文档
    url(r"^swagger/$", schema_view.with_ui("swagger"), name="schema-swagger-ui"),
    url(r"^api_docs/$", schema_view.with_ui("redoc"), name="schema-docs"),
]
