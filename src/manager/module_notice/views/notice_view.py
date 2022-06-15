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
from rest_framework.response import Response

from common.drf.decorator import biz_id
from common.drf.view_set import BaseAllViewSet
from src.manager.module_notice.models import NoticeGroupModel, TriggerModel
from src.manager.module_notice.proto.notice import (
    NoticeGroupViewSerializer,
    ReqPostNoticeGroupViewSerializer,
    notice_group_create_docs,
    notice_group_delete_docs,
    notice_group_list_docs,
    notice_group_retrieve_docs,
    notice_group_update_docs,
)


@method_decorator(name="list", decorator=notice_group_list_docs)
@method_decorator(name="retrieve", decorator=notice_group_retrieve_docs)
@method_decorator(name="create", decorator=notice_group_create_docs)
@method_decorator(name="update", decorator=notice_group_update_docs)
@method_decorator(name="destroy", decorator=notice_group_delete_docs)
class NoticeGroupViewSet(BaseAllViewSet):

    queryset = NoticeGroupModel.objects.all()
    serializer_class = NoticeGroupViewSerializer
    create_serializer_class = ReqPostNoticeGroupViewSerializer
    update_serializer_class = ReqPostNoticeGroupViewSerializer
    filterset_class = NoticeGroupModel.OpenApiFilter

    @biz_id
    def list(self, request, *args, **kwargs):
        """
        查询触发器
        """
        return super().list(self, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        查询单个的所有
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        instance = self.get_object()
        trigger_obj = TriggerModel.objects.get(pk=instance.id)
        data = {
            "name": instance.name,
            "biz_id": instance.biz_id,
            "group_type": instance.group_type,
            "group_value": instance.group_value,
            "trigger_name": trigger_obj.name,
            "trigger_key": trigger_obj.trigger_key,
            "im_platform": trigger_obj.im_platform,
            "im_type": trigger_obj.im_type,
            "trigger_info": trigger_obj.info,
            "description": instance.description,
            "created_by": instance.created_by,
            "created_at": instance.created_at,
        }
        return Response(data)
