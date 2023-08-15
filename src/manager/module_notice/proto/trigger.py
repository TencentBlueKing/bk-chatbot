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

from common.drf.field import BizId, DefaultFiled
from common.drf.serializers import BaseRspSerializer
from common.utils.m_uuid import get_random_str
from src.manager.module_notice.models import TriggerModel
from src.manager.module_notice.proto import notice_tag
from src.manager.module_other.models import IMTypeModel


class TriggerKey(DefaultFiled):
    @DefaultFiled.set_self_value
    def set_context(self, instance):
        """
        设置默认值
        """
        payload = instance.context["request"].payload
        im_platform = payload.get("im_platform")
        im_type = payload.get("im_type")
        im_objects = IMTypeModel.objects.filter(platform=im_platform, im_type=im_type).first()
        if not im_objects:
            raise Exception("缺失im类型")
        return f"{im_objects.alias}-{get_random_str()}"


class ImTypeId(DefaultFiled):
    @DefaultFiled.set_self_value
    def set_context(self, instance):
        """
        设置默认 im_type_id
        @param instance:
        @return:
        """
        payload = instance.context["request"].payload
        im_platform = payload.get("im_platform")
        im_type = payload.get("im_type")
        im_objects = IMTypeModel.objects.filter(platform=im_platform, im_type=im_type).first()
        return im_objects.im_type_id


class TriggerViewSerializer(serializers.ModelSerializer):
    """
    触发器验证器
    """

    info = serializers.DictField(label="触发器key")

    class Meta:
        model = TriggerModel
        fields = [
            "id",
            "name",
            "trigger_key",
            "im_platform",
            "im_type",
            "info",
            "biz_id",
            "created_by",
            "created_at",
            "updated_at",
        ]


class ReqPostTriggerViewSerializer(TriggerViewSerializer):
    """
    添加
    """

    biz_id = serializers.HiddenField(default=BizId())
    trigger_key = serializers.HiddenField(default=TriggerKey())
    im_type_id = serializers.HiddenField(default=ImTypeId())

    class Meta:
        model = TriggerModel
        fields = [
            "id",
            "name",
            "biz_id",
            "im_platform",
            "im_type",
            "info",
            "trigger_key",
            "im_type_id",
        ]


class ReqPutTriggerViewSerializer(TriggerViewSerializer):
    """
    修改
    """

    class Meta:
        model = TriggerModel
        fields = ["name", "info"]


# 查询响应
class RspListTriggerSerializer(BaseRspSerializer):
    count = serializers.IntegerField(label="数量")
    data = serializers.ListField(child=TriggerViewSerializer())


# 添加响应
class RspCreateTriggerSerializer(BaseRspSerializer):
    data = TriggerViewSerializer()


#######################################

trigger_list_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="触发器-查询",
    responses={200: RspListTriggerSerializer()},
)

trigger_create_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="触发器-添加",
    responses={200: RspListTriggerSerializer()},
)

trigger_update_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="触发器-修改",
    responses={200: BaseRspSerializer()},
)

trigger_delete_docs = swagger_auto_schema(
    tags=notice_tag,
    operation_id="触发器-删除",
    responses={200: BaseRspSerializer()},
)
