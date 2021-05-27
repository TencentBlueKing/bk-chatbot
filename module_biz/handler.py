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

from module_api.iaas.redis_client import RedisClient
from module_biz.models import ChatBindBusiness


class GroupBindHandler:
    def __init__(self, chat_group_id=0):
        self.chat_group_id = chat_group_id

    def group_bind_exists(self):
        return ChatBindBusiness.objects.filter(
            chat_group_id=self.chat_group_id,
            is_deleted=0,
        ).exists()

    def update_bind(self, chat_bot_type, biz_id, biz_name):
        ChatBindBusiness.objects.filter(
            chat_group_id=self.chat_group_id,
            is_deleted=0,
        ).update(chat_bot_type=chat_bot_type, biz_id=biz_id, biz_name=biz_name)

    def hash_set_redis_data(self, biz_id, name_space):
        """
        设置redis中的群聊ID信息
        """
        RedisClient().hash_set(name_space, self.chat_group_id, biz_id)
