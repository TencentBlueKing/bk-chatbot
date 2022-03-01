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


class BaseSerializer(serializers.Serializer):
    """
    基础
    """

    page = serializers.IntegerField(required=False, label="页码")
    pagesize = serializers.IntegerField(required=False, label="每页数据量")
    start_time = serializers.CharField(required=False, label="开始时间")
    end_time = serializers.CharField(required=False, label="结束时间")


class BaseModelSerializer(serializers.ModelSerializer):
    """
    基础
    """

    pass


class BaseRspSerializer(serializers.Serializer):
    result = serializers.BooleanField(label="结果是否正确")
    code = serializers.IntegerField(label="状态码")
    message = serializers.CharField(label="返回信息")
    request_id = serializers.CharField(label="request_id")
    data = serializers.JSONField(label="数据")
