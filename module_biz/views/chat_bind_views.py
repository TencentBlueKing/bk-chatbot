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
from common.pagination import ResultsSetPagination
from module_biz.constants import CHAT_BOT_USE_SPACE
from module_biz.control.permission import BizPermission
from module_biz.control.throttle import BizThrottle
from module_biz.handler import GroupBindHandler
from module_biz.models import ChatBindBusiness
from module_biz.serializers import GroupBindBizSerializer


class ChatBindViewSet(APIModelViewSet, ValidationMixin):
    """
    群聊绑定业务
    """

    queryset = ChatBindBusiness.objects.all()
    serializer_class = GroupBindBizSerializer
    filter_fields = {
        "chat_group_id": ["exact"],
        "chat_bot_type": ["exact"],
        "biz_id": ["exact"],
        "created_by": ["exact"],
        "is_deleted": ["exact"],
    }
    ordering_fields = ["biz_id", "created_at", "updated_at", "created_by"]
    ordering = "-created_at"
    permission_classes = (BizPermission,)
    throttle_classes = (BizThrottle,)
    pagination_class = ResultsSetPagination

    def perform_create(self, serializer):
        """新增后同步到redis"""
        super().perform_create(serializer)
        GroupBindHandler(serializer.instance.chat_group_id).hash_set_redis_data(
            serializer.instance.biz_id,
            CHAT_BOT_USE_SPACE,
        )
        ChatBindBusiness.objects.filter(
            chat_group_id=serializer.instance.chat_group_id
        ).update(
            chat_index_id=serializer.instance.chat_group_id,
        )

    def perform_update(self, serializer):
        """
        更新后同步到redis
        """
        super().perform_update(serializer)
        GroupBindHandler(serializer.instance.chat_group_id).hash_set_redis_data(
            serializer.instance.biz_id,
            CHAT_BOT_USE_SPACE,
        )
        ChatBindBusiness.objects.filter(
            chat_group_id=serializer.instance.chat_group_id
        ).update(
            chat_index_id=serializer.instance.chat_group_id,
        )

    def perform_destroy(self, instance):
        """
        删除后同步到redis
        """
        super().perform_destroy(instance)
        GroupBindHandler(instance.chat_index_id).hash_set_redis_data(
            "-1",
            CHAT_BOT_USE_SPACE,
        )
        ChatBindBusiness.objects.filter(chat_group_id=instance.chat_group_id).update(
            chat_group_id=f"{str(instance.chat_group_id)}_{instance.biz_id}",
        )
