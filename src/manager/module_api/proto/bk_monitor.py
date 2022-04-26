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


class BkMonitorSerializer(Serializer):
    biz_id = serializers.IntegerField(required=True, label="业务ID")
    ip = serializers.IPAddressField(required=True, allow_blank=True, label="特色ID")
    metric = serializers.CharField(required=True, allow_blank=True, label="指标")
    bk_cloud_id = serializers.IntegerField(required=False, label="云区域ID", default=0)
    start_timestamp = serializers.IntegerField(required=True, label="开始时间戳")
    end_timestamp = serializers.IntegerField(required=True, label="结束时间戳")


class BkHostSerializer(Serializer):
    biz_id = serializers.IntegerField(required=True, label="业务ID")
    set_ids = serializers.JSONField(label="集群列表", required=False)
    module_ids = serializers.JSONField(label="模块列表", required=False)
    ip_keyword = serializers.CharField(required=False, allow_blank=True, label="ip关键字")
