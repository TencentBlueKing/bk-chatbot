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

import json

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response

from common.control.throttle import ChatBotThrottle
from common.drf.generic import BaseViewSet
from common.redis import RedisClient
from src.manager.handler.api.bk_itsm_flex import ItsmFlex
from src.manager.module_api.constants import ITSM_FLEX_SERVICE_CATALOGUE_CACHE_KEY
from src.manager.module_api.proto import api_tag


class ItsmViewSet(BaseViewSet):
    """
    ITSM 相关接口
    """

    throttle_classes = (ChatBotThrottle,)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema(tags=api_tag, operation_id="查询ITSM服务目录")
    @action(detail=False, methods=["GET"])
    def list_service_catalogue(self, request, *args, **kwargs):
        """获取服务目录列表（前端下拉选项）"""
        username = request.user.username

        # 是否强制刷新缓存
        force_refresh = request.query_params.get("force_refresh") == "1"

        rc = RedisClient()
        service_catalogues = None if force_refresh else rc.get(ITSM_FLEX_SERVICE_CATALOGUE_CACHE_KEY)
        if not service_catalogues:
            result = ItsmFlex.get_service_catalogue_flatten(username=username)
            ok = result.get("result", False)
            if not ok:
                err_msg = result.get("message", "获取ITSM服务目录失败")
                raise Exception(err_msg)
            service_catalogues = result.get("data", [])
            ttl = settings.ITSM_FLEX_SERVICE_CATALOGUE_TTL
            rc.redis_client.set(ITSM_FLEX_SERVICE_CATALOGUE_CACHE_KEY, json.dumps(service_catalogues), ex=ttl)
        data = [{"key": item.get("code_path"), "name": item.get("name_path")} for item in service_catalogues]

        return Response(data)
