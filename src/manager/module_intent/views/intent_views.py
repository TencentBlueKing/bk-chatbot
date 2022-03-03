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
            payload = self.request.payload
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
    def fetch_intent_count(self, request, *args, **kwargs):
        """
        获取意图数
        """
        count = len(Intent.query_intent_list(biz_id=int(kwargs.get("biz")), is_deleted=False))
        data = {"data": {"count": count}}
        return Response(data)
