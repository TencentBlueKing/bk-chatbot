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


from blueapps.account.decorators import login_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema

from common.drf.view_set import BaseGetViewSet
from common.perm.permission import check_permission
from src.manager.module_api.proto import api_tag
from src.manager.module_api.proto.biz_variable import BizVariableViewSerializer
from src.manager.module_biz.models import BizVariableModel


@method_decorator(name="list", decorator=swagger_auto_schema(tags=api_tag, operation_id="查询业务变量"))
class BizVariableViewSet(BaseGetViewSet):
    """
    业务变量
    """

    queryset = BizVariableModel.objects.all()
    serializer_class = BizVariableViewSerializer
    filterset_class = BizVariableModel.OpenApiFilter

    @login_exempt
    @csrf_exempt
    @check_permission()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
