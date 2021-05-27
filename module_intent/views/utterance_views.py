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

from common.generic import APIModelViewSet
from common.generic import ValidationMixin
from module_intent.control.permission import IntentPermission
from module_intent.control.serializers import UtterancesSerializer
from module_intent.control.throttle import IntentThrottle
from module_intent.models import Utterances


class UtterancesViewSet(APIModelViewSet, ValidationMixin):
    """
    语料操作
    """

    queryset = Utterances.objects.all()
    serializer_class = UtterancesSerializer
    filter_fields = {"biz_id": ["exact"], "index_id": ["exact"]}
    ordering_fields = ["biz_id", "index_id"]
    ordering = "-updated_at"
    permission_classes = (IntentPermission,)
    throttle_classes = (IntentThrottle,)
