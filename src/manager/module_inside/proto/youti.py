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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers

from common.drf.serializers import BaseRspSerializer
from src.manager.module_inside.proto import inside_tag


class ReqGetProductUsersSerializer(serializers.Serializer):
    """
    查询业务下的人员信息
    """

    cc_id = serializers.CharField(label="cc_id", required=False)
    code_allow_null = serializers.ChoiceField(label="code_allow_null", required=False, choices=["0", "1"])


class RspGetProductUsersSerializer(BaseRspSerializer):
    """
    业务下人员信息返回
    """

    class RspGetProductUsersSerializerData(serializers.Serializer):
        class RspGetProductUsersSerializerDataResult(serializers.Serializer):
            username = serializers.CharField()
            code = serializers.CharField()
            display_name = serializers.CharField()
            departments = serializers.CharField()

        result = serializers.ListField(child=RspGetProductUsersSerializerDataResult())
        count = serializers.IntegerField(label="业务数量")

    data = RspGetProductUsersSerializerData()


############################################################
get_product_user_docs = swagger_auto_schema(
    tags=inside_tag,
    operation_id="youti-查询业务下的人员",
    query_serializer=ReqGetProductUsersSerializer(),
    responses={200: RspGetProductUsersSerializer()},
)
