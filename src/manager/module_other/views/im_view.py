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

from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.response import Response

from common.drf.view_set import BaseGetViewSet, BaseViewSet
from src.manager.module_other.models import IMTypeModel
from src.manager.module_other.proto.im import (
    ImSerializer,
    im_list_docs,
    im_platform_list_docs,
)


@method_decorator(name="list", decorator=im_list_docs)
class IMViewSet(BaseGetViewSet):
    queryset = IMTypeModel.objects.all()
    serializer_class = ImSerializer
    filterset_class = IMTypeModel.OpenApiFilter


@method_decorator(name="platform", decorator=im_platform_list_docs)
class IMPlatFormViewSet(BaseViewSet):
    @action(detail=False, methods=["GET"])
    def platform(self, request, **kwargs):
        """
        平台
        @return:
        """
        data = IMTypeModel.query_im_platform()
        return Response({"data": data})
