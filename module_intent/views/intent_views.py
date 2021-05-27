# -*- coding: utf-8 -*-
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
from rest_framework.decorators import action
from rest_framework.response import Response

from common.generic import APIModelViewSet
from common.generic import ValidationMixin
from common.pagination import ResultsSetPagination
from common.utils.users import get_request_user
from module_api.iaas.http import init_views
from module_intent.control.permission import IntentPermission
from module_intent.control.serializers import IntentSerializer
from module_intent.control.throttle import IntentThrottle
from module_intent.models import Intent
from module_intent.models import Task
from module_intent.models import Utterances


class IntentViewSet(APIModelViewSet, ValidationMixin):
    """
    意图接入
    """

    queryset = Intent.objects.all()
    serializer_class = IntentSerializer
    filter_fields = {
        'biz_id': ['exact'],
        'index_id': ['exact'],
        'intent_name': ['exact'],
        'status': ['exact'],
        'is_commit': ['exact'],
        'created_by': ['exact'],
        'is_deleted': ['exact'],
    }
    ordering_fields = [
        'biz_id',
        'biz_name',
        'bot_id',
        'created_by',
        'updated_at',
    ]
    ordering = '-updated_at'
    permission_classes = (IntentPermission,)
    throttle_classes = (IntentThrottle,)
    pagination_class = ResultsSetPagination

    def perform_create(self, serializer):
        """新增意图后续动作"""
        super().perform_create(serializer)
        with transaction.atomic():
            Utterances.create_utterance(
                biz_id=int(serializer.instance.biz_id),
                index_id=serializer.instance.id,
                content=self.request.data.get('utterances', ''),
            )
            Task.create_task(
                biz_id=int(serializer.instance.biz_id),
                index_id=serializer.instance.id,
                platform=self.request.data.get('platform', ''),
                task_id=str(self.request.data.get('task_id', '')),
                slots=self.request.data.get('slots', []),
                activities=self.request.data.get('activities', []),
                source=self.request.data.get('source', ''),
            )

    def perform_update(self, serializer):
        """
        更新意图的后续动作
        """
        super().perform_update(serializer)
        with transaction.atomic():
            Utterances.update_utterance(
                intent_id=serializer.instance.id,
                biz_id=serializer.instance.biz_id,
                index_id=serializer.instance.id,
                content=self.request.data.get('utterances', ''),
            )
            Task.update_task(
                intent_id=serializer.instance.id,
                biz_id=int(serializer.instance.biz_id),
                index_id=serializer.instance.id,
                platform=self.request.data.get('platform', ''),
                task_id=str(self.request.data.get('task_id', '')),
                slots=self.request.data.get('slots', []),
                activities=self.request.data.get('activities', []),
                source=self.request.data.get('source', ''),
            )

    @action(detail=False, methods=['POST'])
    def create_intent(self, request, biz_id):
        """
        创建意图
        """
        req_data, ret_data = init_views(request)
        ret_data = {}
        intent, created = Intent.create_intent(
            biz_id=int(biz_id),
            index_id=req_data['index_id'],
            intent_name=req_data['intent_name'],
        )

        if created:
            intent.is_commit = req_data.get('is_commit', True)
            intent.available_user = req_data.get('available_user', [])
            intent.available_group = req_data.get('available_group', [])
            intent.create_by = get_request_user(request)
            intent.save()
            with transaction.atomic():
                Utterances.create_utterance(
                    biz_id=int(biz_id),
                    index_id=intent.pk,
                    content=req_data['utterances'],
                )
                Task.create_task(
                    biz_id=int(biz_id),
                    index_id=intent.pk,
                    platform=req_data['platform'],
                    task_id=str(req_data['task_id']),
                    slots=req_data.get('slots', []),
                    activities=req_data.get('activities', []),
                    source=req_data['source'],
                )

        elif req_data.get('id', -1) != -1:
            with transaction.atomic():
                Utterances.update_utterance(
                    intent.id,
                    biz_id=int(biz_id),
                    index_id=intent.pk,
                    content=req_data['utterances'],
                )
                Task.update_task(
                    intent.id,
                    biz_id=int(biz_id),
                    index_id=intent.pk,
                    platform=req_data['platform'],
                    task_id=str(req_data['task_id']),
                    slots=req_data.get('slots', []),
                    activities=req_data.get('activities', []),
                    source=req_data['source'],
                )
        else:
            ret_data['result'] = False
            ret_data['message'] = '创建失败，eg：名称重复'
            return Response(ret_data)

        return Response(ret_data)

    @action(detail=False, methods=['POST'])
    def fetch_intent_count(self, request, *args, **kwargs):
        """
        获取意图数
        """
        return Response(
            {
                'count': len(
                    Intent.query_intent_list(
                        biz_id=int(kwargs.get('biz_id')), is_deleted=False,
                    ),
                ),
            },
        )
