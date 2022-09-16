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

from common.drf.decorator import set_cookie_biz_id
from common.drf.validation import validation
from common.drf.view_set import BaseAllViewSet, BaseGetViewSet, BaseViewSet
from common.http.request import get_request_biz_id
from common.perm.permission import login_exempt_with_perm
from src.manager.module_notice.handler.deal_notice_log import NoticeLog
from src.manager.module_notice.handler.notice import send_msg_to_notice_group
from src.manager.module_notice.handler.webhook import (
    get_notice_group_by_webhook_key,
    make_notice_group_webhook_url,
)
from src.manager.module_notice.models import NoticeGroupModel, TriggerModel
from src.manager.module_notice.proto.notice import (
    NoticeGroupViewGWSerializer,
    NoticeGroupViewSerializer,
    ReqGetNoticeGroupGWViewSerializer,
    ReqPostNoticeGroupSendMsgGWViewSerializer,
    ReqPostNoticeGroupViewSerializer,
    ReqPostNoticeSendWebhookGWViewSerializer,
    ReqPutNoticeGroupViewSerializer,
    notice_group_create_docs,
    notice_group_delete_docs,
    notice_group_list_docs,
    notice_group_retrieve_docs,
    notice_group_update_docs,
    notice_log_list_docs,
)


@method_decorator(name="list", decorator=notice_group_list_docs)
@method_decorator(name="list", decorator=set_cookie_biz_id())
@method_decorator(name="retrieve", decorator=notice_group_retrieve_docs)
@method_decorator(name="create", decorator=notice_group_create_docs)
@method_decorator(name="update", decorator=notice_group_update_docs)
@method_decorator(name="destroy", decorator=notice_group_delete_docs)
class NoticeGroupViewSet(BaseAllViewSet):
    queryset = NoticeGroupModel.objects.all()
    serializer_class = NoticeGroupViewSerializer
    create_serializer_class = ReqPostNoticeGroupViewSerializer
    update_serializer_class = ReqPutNoticeGroupViewSerializer
    filterset_class = NoticeGroupModel.OpenApiFilter

    def retrieve(self, request, *args, **kwargs):
        """
        查询单个的所有
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        instance = self.get_object()
        trigger_obj = TriggerModel.objects.get(pk=instance.trigger_id)
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = []
            for group in serializer.data:
                data.append({"webhook_url": make_notice_group_webhook_url([group.get("id")]), **group})
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = []
        for group in serializer.data:
            data.append({"webhook_url": make_notice_group_webhook_url([group.get("id")]), **group})

        return Response(data)


class NoticeGroupGwViewSet(BaseGetViewSet):
    schema = None
    queryset = NoticeGroupModel.objects.all()
    serializer_class = NoticeGroupViewGWSerializer
    filterset_class = NoticeGroupModel.OpenApiFilter

    @login_exempt_with_perm
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @validation(ReqGetNoticeGroupGWViewSerializer)
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)


class NoticeSendGwViewSet(BaseViewSet):
    schema = None

    @login_exempt_with_perm
    @action(detail=False, methods=["POST"])
    @validation(ReqPostNoticeGroupSendMsgGWViewSerializer)
    def notice_group(self, request, *args, **kwargs):
        payload = request.payload
        notice_group_id_list = payload.get("notice_group_id_list")
        msg_type = payload.get("msg_type")
        msg_content = payload.get("msg_content")
        send_result = send_msg_to_notice_group(notice_group_id_list, msg_type, msg_content)
        if not send_result["result"]:
            return Response({"message": send_result["message"]}, exception=True)
        return Response({"data": []})

    @action(detail=False, methods=["POST"])
    @validation(ReqPostNoticeSendWebhookGWViewSerializer)
    def webhook(self, request, *args, **kwargs):
        key = request.query_params.get("key")
        payload = request.payload
        msg_type = payload.get("msg_type")
        msg_content = payload.get("msg_content")

        if not key:
            return Response({"message": "webhook key不能为空"}, exception=True)

        result, data = get_notice_group_by_webhook_key(key)
        if not result:
            return Response({"message": data}, exception=True)

        send_result = send_msg_to_notice_group(data, msg_type, msg_content)
        if not send_result["result"]:
            return Response({"message": send_result["message"]}, exception=True)
        return Response({"data": []})


@method_decorator(name="list", decorator=notice_log_list_docs)
class NoticeLogViewSet(BaseViewSet):
    """
    通知历史展示
    """

    def list(self, request, *args, **kwargs):
        """
        业务查询
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        payload = request.payload
        biz_id = get_request_biz_id(request)
        # 获取业务信息错误
        if not biz_id:
            raise ValueError("get biz_id is error")
        notice_log = NoticeLog(biz_id, **payload)
        # 获取数据
        count = notice_log.get_count()
        data = notice_log.get_data()
        data = {"data": data, "count": count}
        return Response(data)
