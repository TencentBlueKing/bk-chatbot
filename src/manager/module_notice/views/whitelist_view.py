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

from common.drf.decorator import biz_id
from common.drf.view_set import BaseManageViewSet
from src.manager.common.perm import check_biz_ops
from src.manager.module_notice.models import WhitelistModel
from src.manager.module_notice.proto.whitelist import (
    ReqPostWhiteListViewSerializer,
    ReqPutWhiteListViewSerializer,
    WhiteListViewSerializer,
    white_list_create_docs,
    white_list_del_docs,
    white_list_list_docs,
    white_list_update_docs,
)


@method_decorator(name="list", decorator=white_list_list_docs)
@method_decorator(name="create", decorator=white_list_create_docs)
@method_decorator(name="update", decorator=white_list_update_docs)
@method_decorator(name="destroy", decorator=white_list_del_docs)
class WhiteListViewSet(BaseManageViewSet):

    queryset = WhitelistModel.objects.all()
    serializer_class = WhiteListViewSerializer
    create_serializer_class = ReqPostWhiteListViewSerializer
    update_serializer_class = ReqPutWhiteListViewSerializer
    filterset_class = WhitelistModel.OpenApiFilter

    @biz_id
    def list(self, request, *args, **kwargs):
        """
        查询
        """
        return super().list(request, *args, **kwargs)

    @check_biz_ops
    def create(self, request, *args, **kwargs):
        """
        添加
        """
        return super().create(request, *args, **kwargs)

    @check_biz_ops
    def update(self, request, *args, **kwargs):
        """
        修改
        """
        return super().update(request, *args, **kwargs)

    @check_biz_ops
    def destroy(self, request, *args, **kwargs):
        """
        删除
        """
        return super().destroy(request, *args, **kwargs)
