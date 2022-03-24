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

from common.drf.view_set import BaseGetViewSet
from src.manager.module_other.models import VersionModel
from src.manager.module_other.proto.version import VersionSerializer, version_list_docs


@method_decorator(name="list", decorator=version_list_docs)
class VersionViewSet(BaseGetViewSet):
    queryset = VersionModel.objects.all()
    serializer_class = VersionSerializer
    filterset_class = VersionModel.OpenApiFilter
