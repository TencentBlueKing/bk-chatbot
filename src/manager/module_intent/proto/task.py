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

from common.constants import TASK_PLATFORM_CHOICES
from module_intent.models import Task


class TaskSerializer(serializers.ModelSerializer):
    biz_id = serializers.IntegerField(required=True, label="业务ID")
    index_id = serializers.IntegerField(required=True, label="索引ID")
    platform = serializers.ChoiceField(
        required=True,
        label="平台名称",
        choices=TASK_PLATFORM_CHOICES,
    )
    task_id = serializers.CharField(required=True, label="任务ID")
    activities = serializers.ListField(required=True, label="节点信息")
    slots = serializers.ListField(required=True, label="槽位信息")
    source = serializers.CharField(required=True, label="任务元数据")
    script = serializers.CharField(required=True, label="执行脚本信息")

    class Meta:
        model = Task
        fields = "__all__"
