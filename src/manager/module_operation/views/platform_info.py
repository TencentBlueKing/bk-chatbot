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
from django.db.models import Count

from common.drf.view_set import BaseViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from common.http.request import get_request_biz_id
from src.manager.module_intent.models import Task


class PlatformViewSet(BaseViewSet):
    schema = None

    @action(detail=False, methods=["GET"])
    def config_info(self, request, *args, **kwargs):
        biz_id = get_request_biz_id(request)
        platform_map = {"0": "默认", "1": "作业平台", "2": "标准运维", "3": "蓝盾", "4": "自定义"}
        queryset = (
            Task.objects.filter(biz_id=biz_id, is_deleted=False).values("platform").annotate(config_num=Count("id"))
        )
        data = []
        for item in queryset:
            data.append({"item": platform_map[item["platform"]], "value": item["config_num"]})
        return Response({"data": data})
