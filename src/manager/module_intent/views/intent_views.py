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

from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.response import Response
from common.control.throttle import ChatBotThrottle
from common.drf.view_set import BaseManageViewSet
from common.drf.validation import validation
from src.manager.module_intent.control.permission import IntentPermission
from src.manager.module_intent.models import Intent, Task, Utterances
from src.manager.module_intent.proto.intent import (
    IntentSerializer,
    ReqGetIntentSerializer,
    intent_count_docs,
    intent_create_docs,
    intent_del_docs,
    intent_list_docs,
    intent_update_docs,
    ReqPostBatchUpdateAvailableUserSerializers,
    ReqPostBatchUpdateIntentTagSerializers,
)


@method_decorator(name="create", decorator=intent_create_docs)
@method_decorator(name="list", decorator=intent_list_docs)
@method_decorator(name="update", decorator=intent_update_docs)
@method_decorator(name="destroy", decorator=intent_del_docs)
@method_decorator(name="fetch_intent_count", decorator=intent_count_docs)
class IntentViewSet(BaseManageViewSet):
    """
    意图接入
    """

    queryset = Intent.objects.all()
    serializer_class = IntentSerializer
    list_serializer_class = ReqGetIntentSerializer
    filterset_class = Intent.OpenApiFilter
    ordering_fields = ["biz_id", "biz_name", "bot_id", "created_by", "updated_at"]
    ordering = "-updated_at"
    permission_classes = (IntentPermission,)
    throttle_classes = (ChatBotThrottle,)

    def list(self, request, *args, **kwargs):
        request.query_params._mutable = True
        # available_user查询
        available_user = self.request.payload.get("available_user", None)
        if available_user:
            request.query_params["available_user"] = f'"{self.request.payload.get("available_user")}"'
        # available_group 查询
        available_group = self.request.payload.get("available_group", None)
        if available_group:
            request.query_params["available_group"] = f'"{self.request.payload.get("available_group")}"'

        response = super().list(self, request, *args, **kwargs)
        data = response.data
        intent_id_list = [i["id"] for i in data["data"]]
        uqs = Utterances.objects.filter(index_id__in=intent_id_list).values("content", "index_id")
        intent_utterances_dict = {i["index_id"]: i["content"] for i in uqs}
        for _intent in data["data"]:
            _intent["utterances_list"] = intent_utterances_dict.get(_intent["id"], [])
        return response

    def perform_create(self, serializer):
        """
        新增意图后续动作
        """
        with transaction.atomic():
            super().perform_create(serializer)

            payload = self.request.payload
            Utterances.create_utterance(
                biz_id=int(serializer.instance.biz_id),
                index_id=serializer.instance.id,
                content=payload.get("utterances", ""),
            )
            # fix前端传过来的source为字符串的问题
            source = payload.get("source", "")
            if isinstance(source, str) and isinstance(eval(source), dict):
                source = eval(source)
            Task.create_task(
                biz_id=int(serializer.instance.biz_id),
                index_id=serializer.instance.id,
                platform=payload.get("platform", ""),
                project_id=payload.get("project_id", ""),
                task_id=payload.get("task_id", ""),
                slots=payload.get("slots", []),
                activities=payload.get("activities", []),
                source=source,
            )

    def perform_update(self, serializer):
        """
        更新意图的后续动作
        """

        with transaction.atomic():
            super().perform_update(serializer)
            payload: dict = self.request.payload

            # 如果只有status则不进行后面的操作
            if len(payload.keys()) == 1 and list(payload.keys())[0] == "status":
                return

            Utterances.update_utterance(
                intent_id=serializer.instance.id,
                biz_id=serializer.instance.biz_id,
                index_id=serializer.instance.id,
                content=payload.get("utterances", ""),
            )
            # fix前端传过来的source为字符串的问题
            source = payload.get("source", "")
            if isinstance(source, str) and isinstance(eval(source), dict):
                source = eval(source)
            Task.update_task(
                intent_id=serializer.instance.id,
                biz_id=int(serializer.instance.biz_id),
                index_id=serializer.instance.id,
                project_id=payload.get("project_id", ""),
                platform=payload.get("platform", ""),
                task_id=payload.get("task_id", ""),
                slots=payload.get("slots", []),
                activities=payload.get("activities", []),
                source=source,
            )

    @action(detail=False, methods=["POST"])
    @validation(ReqPostBatchUpdateAvailableUserSerializers)
    def batch_update_available_user(self, request, *args, **kwargs):
        payload = request.payload
        intent_id_list = payload.get("intent_id_list")
        operator_type = payload.get("operator_type")
        operator_user_set = set(payload.get("operator_user_list"))

        filter_queryset = self.queryset.filter(id__in=intent_id_list)
        update_intent_list = []
        for intent in filter_queryset:
            if operator_type == "add":
                intent.available_user = list(set(intent.available_user) | operator_user_set)
            if operator_type == "delete":
                intent.available_user = list(set(intent.available_user) - operator_user_set)
            update_intent_list.append(intent)
        Intent.objects.bulk_update(update_intent_list, ["available_user"])
        return Response({"data": []})

    @action(detail=False, methods=["POST"])
    @validation(ReqPostBatchUpdateAvailableUserSerializers)
    def batch_update_developer(self, request, *args, **kwargs):
        payload = request.payload
        intent_id_list = payload.get("intent_id_list")
        operator_type = payload.get("operator_type")
        operator_user_set = set(payload.get("operator_user_list"))

        filter_queryset = self.queryset.filter(id__in=intent_id_list)
        update_intent_list = []
        for intent in filter_queryset:
            if operator_type == "add":
                intent.developer = list(set(intent.developer) | operator_user_set)
            if operator_type == "delete":
                intent.developer = list(set(intent.developer) - operator_user_set)
            update_intent_list.append(intent)
        Intent.objects.bulk_update(update_intent_list, ["developer"])
        return Response({"data": []})

    @action(detail=False, methods=["POST"])
    @validation(ReqPostBatchUpdateIntentTagSerializers)
    def batch_update_intent_tag(self, request, *args, **kwargs):
        payload = request.payload
        intent_id_list = payload.get("intent_id_list")
        tag_name = payload.get("tag_name")

        filter_queryset = self.queryset.filter(id__in=intent_id_list)
        update_intent_list = []
        for intent in filter_queryset:
            intent.tag_name = tag_name
            update_intent_list.append(intent)
        Intent.objects.bulk_update(update_intent_list, ["tag_name"])
        return Response({"data": []})

    @action(detail=False, methods=["POST"])
    def fetch_intent_count(self, request, *args, **kwargs):
        """
        获取意图数
        """
        count = len(Intent.query_intent_list(biz_id=int(kwargs.get("biz")), is_deleted=False))
        data = {"data": {"count": count}}
        return Response(data)
