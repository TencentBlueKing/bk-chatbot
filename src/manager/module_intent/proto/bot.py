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

from rest_framework import serializers

from common.constants import CHAT_BOT_TYPES
from src.manager.module_intent.models import Bot


class BotSerializer(serializers.ModelSerializer):
    biz_id = serializers.IntegerField(required=True, label="业务ID")
    biz_name = serializers.CharField(required=True, label="业务名称")
    bot_id = serializers.CharField(required=True, label="业务名称")
    bot_name = serializers.CharField(required=True, label="业务名称")
    bot_type = serializers.ChoiceField(
        required=True,
        label="业务名称",
        choices=CHAT_BOT_TYPES,
    )

    class Meta:
        model = Bot
        fields = (
            "id",
            "biz_id",
            "biz_name",
            "bot_id",
            "bot_name",
            "bot_type",
            "created_by",
            "created_at",
            "updated_at",
        )
