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


class DescribeJob(Serializer):
    """
    作业平台
    """

    id = serializers.CharField(required=True, label="作业平台执行方案id")


class DescribeSops(Serializer):
    """
    标准运维任务明细
    """

    id = serializers.CharField(required=True, label="标准运维流程id")


class SopsPreviewTaskTree(Serializer):
    """
    标准运维预览任务树
    """
    template_id = serializers.CharField(required=True, label="流程模版ID")
    exclude_task_nodes_id = serializers.ListSerializer(required=True, child=serializers.CharField(), allow_empty=True,
                                                       label="需要移除的可选节点 ID 列表")


class DescribeSopsSchemes(Serializer):
    """
    标准运维任务分组信息
    """

    id = serializers.CharField(required=True, label="标准运维流程id")


class DescribeDevopsPipelinesStartInfo(Serializer):
    """
    蓝盾流水请求参数
    """

    pipeline_id = serializers.CharField(required=True, label="蓝盾的流水线ID")
