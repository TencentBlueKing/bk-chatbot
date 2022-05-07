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
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from common.drf.view_set import BaseUpdateViewSet
from common.perm.permission import check_permission
from src.manager.module_intent.models import Intent, Task, Utterances
from src.manager.module_intent.proto.intent import IntentSerializer, intent_update_docs


@method_decorator(name="update", decorator=intent_update_docs)
class IntentViewSet(BaseUpdateViewSet):
    """
    意图接入
    """

    queryset = Intent.objects.all()
    serializer_class = IntentSerializer

    @login_exempt
    @csrf_exempt
    @check_permission()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

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
