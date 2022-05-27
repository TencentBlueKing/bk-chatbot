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

from common.drf.view_set import BaseManageViewSet
from src.manager.module_biz.models import BizVariableModel
from src.manager.module_biz.proto.biz_variable import (
    BizVariableViewSerializer,
    ReqPostBizVariableViewSerializer,
    biz_variable_create_docs,
    biz_variable_delete_docs,
    biz_variable_list_docs,
    biz_variable_update_docs,
)


@method_decorator(name="list", decorator=biz_variable_list_docs)
@method_decorator(name="create", decorator=biz_variable_create_docs)
@method_decorator(name="update", decorator=biz_variable_update_docs)
@method_decorator(name="destroy", decorator=biz_variable_delete_docs)
class BizVariableViewSet(BaseManageViewSet):
    """
    业务信息
    """

    queryset = BizVariableModel.objects.all()
    serializer_class = BizVariableViewSerializer
    create_serializer_class = ReqPostBizVariableViewSerializer
    update_serializer_class = ReqPostBizVariableViewSerializer
    filterset_class = BizVariableModel.OpenApiFilter
