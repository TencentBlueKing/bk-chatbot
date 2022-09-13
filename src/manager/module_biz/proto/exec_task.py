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
from rest_framework.serializers import Serializer

from common.constants import TAK_PLATFORM_JOB, TAK_PLATFORM_SOPS, TAK_PLATFORM_DEVOPS


class ExecTaskListParamsSerializer(Serializer):
    operator = serializers.CharField(required=True, label="操作人")


class ExecTaskDetailParamsSerializer(Serializer):
    operator = serializers.CharField(required=True, label="操作人")
    platform = serializers.ChoiceField(
        required=True, choices=[TAK_PLATFORM_JOB, TAK_PLATFORM_SOPS, TAK_PLATFORM_DEVOPS], label="任务所属平台"
    )


class ExecTaskParamsParamsSerializer(Serializer):
    operator = serializers.CharField(required=True, label="操作人")
    platform = serializers.ChoiceField(
        required=True, choices=[TAK_PLATFORM_JOB, TAK_PLATFORM_SOPS, TAK_PLATFORM_DEVOPS], label="任务所属平台"
    )
