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

from common.drf.field import BizId
from src.manager.module_notice.models import WhitelistModel
from src.manager.module_notice.proto import notice_tag


class WhiteListViewSerializer(serializers.ModelSerializer):
    """
    协议
    """

    whitelist_ip = serializers.IPAddressField()

    class Meta:
        model = WhitelistModel
        fields = ["id", "biz_id", "whitelist_ip", "created_by"]


class ReqPostWhiteListViewSerializer(WhiteListViewSerializer):
    """
    添加
    """

    biz_id = serializers.HiddenField(default=BizId())
    created_by = serializers.HiddenField(default="")


class ReqPutWhiteListViewSerializer(WhiteListViewSerializer):
    """
    修改
    """

    class Meta:
        model = WhitelistModel
        fields = ["id", "whitelist_ip"]


##############################################

white_list_list_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="白名单-查询",
)

white_list_create_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="白名单-添加",
)

white_list_update_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="白名单-修改",
)

white_list_del_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="白名单-删除",
)
