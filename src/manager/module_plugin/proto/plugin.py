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
from rest_framework.serializers import Serializer

from common.drf.serializers import BaseRspSerializer
from src.manager.module_plugin.models import Plugin
from src.manager.module_plugin.proto import plugin_tag


# 插件action
class PluginAction(Serializer):
    """
    插件的动作
    """

    class PluginActionParam(Serializer):
        class PluginActionParamOptions(Serializer):
            id = serializers.CharField(label="id")
            name = serializers.CharField(label="选择名称")

        key = serializers.CharField(label="字段key")
        name = serializers.CharField(label="字段名称")
        desc = serializers.CharField(label="描叙")
        type = serializers.CharField(label="字段类型", required=False, default="input")
        show = serializers.BooleanField(label="是否展示", required=False, default=True)
        required = serializers.BooleanField(label="是否必须", required=False, default=True)
        options = serializers.ListField(label="选项", required=False, child=PluginActionParamOptions())

    key = serializers.CharField(label="路由")
    desc = serializers.CharField(label="描叙")
    time_out = serializers.IntegerField(label="描叙", required=False, default=60)
    run_now = serializers.BooleanField(label="是否立即执行", required=False, default=False)
    params = serializers.ListField(label="字段", child=PluginActionParam())


# 基础
class PluginBaseSerializer(serializers.ModelSerializer):
    plugin_icon = serializers.CharField(label="插件图标")
    plugin_name = serializers.CharField(label="插件名称")
    plugin_addr = serializers.CharField(label="插件地址")
    plugin_desc = serializers.CharField(label="插件描叙")
    plugin_tag = serializers.CharField(label="插件标签")
    plugin_global = serializers.DictField(label="全局变量", required=False)
    actions = serializers.ListField(label="动作", child=PluginAction(), allow_null=True)
    biz_list = serializers.ListField(label="业务选择", child=serializers.CharField())
    developers = serializers.ListField(label="业务选择", child=serializers.CharField())

    class Meta:
        model = Plugin
        fields = [
            "plugin_icon",
            "plugin_name",
            "plugin_addr",
            "plugin_desc",
            "plugin_tag",
            "plugin_status",
            "plugin_global",
            "plugin_type",
            "developers",
            "choose_biz",
            "biz_list",
            "actions",
        ]

    def validate_developers(self, value):
        """
        默认添加开发人员的数据
        :param value:
        :return:
        """
        username = self.context["request"].user.username
        if username not in value:
            value.append(username)
        return value


# plugin视图序列化
class PluginSerializer(PluginBaseSerializer):
    """
    协议
    """

    plugin_key = serializers.CharField(label="插件key")

    class Meta:
        model = Plugin
        fields = [
            "id",
            "plugin_key",
            "plugin_icon",
            "plugin_name",
            "plugin_addr",
            "plugin_desc",
            "plugin_tag",
            "plugin_status",
            "plugin_global",
            "plugin_type",
            "developers",
            "choose_biz",
            "biz_list",
            "actions",
        ]


# 插件管理-单个查询响应
class RspRetrievePluginSerializer(BaseRspSerializer):
    data = PluginSerializer()


# 插件管理-查询多个
class ReqListPluginSerializer(serializers.ModelSerializer):
    biz_list = serializers.ListField(
        label="业务选择",
        child=serializers.CharField(),
    )

    class Meta:
        model = Plugin
        fields = [
            "id",
            "plugin_key",
            "plugin_name",
            "plugin_status",
            "plugin_icon",
            "plugin_exec_count",
            "plugin_lately_count",
            "plugin_type",
            "plugin_tag",
            "biz_list",
            "created_at",
            "created_by",
        ]


# 插件管理-查询响应
class RspListPluginSerializer(BaseRspSerializer):
    count = serializers.IntegerField(label="数量")
    data = serializers.ListField(child=ReqListPluginSerializer())


# 插件管理-添加响应
class RspCreatePluginSerializer(BaseRspSerializer):
    data = PluginSerializer()


# 插件管理-更新
class ReqUpdatePluginSerializer(PluginBaseSerializer):
    plugin_icon = serializers.CharField(label="插件图标", required=False)
    plugin_name = serializers.CharField(label="插件名称", required=False)
    plugin_addr = serializers.CharField(label="插件地址", required=False)
    plugin_desc = serializers.CharField(label="插件描叙", required=False)
    plugin_tag = serializers.CharField(label="插件标签", required=False)
    plugin_global = serializers.DictField(label="全局变量", required=False)
    plugin_status = serializers.IntegerField(label="状态", required=False)
    actions = serializers.ListField(
        label="动作",
        child=PluginAction(),
        allow_null=True,
        required=False,
    )
    biz_list = serializers.ListField(
        label="业务选择",
        child=serializers.CharField(),
        required=False,
    )
    developers = serializers.ListField(
        label="业务选择",
        child=serializers.CharField(),
        required=False,
    )

    def to_representation(self, value):
        return {}


############################################################

plugin_list_docs = swagger_auto_schema(
    tags=plugin_tag,
    operation_id="插件管理-获取",
    responses={200: RspListPluginSerializer()},
)
plugin_private_docs = swagger_auto_schema(
    tags=plugin_tag,
    operation_id="插件管理-获取私人",
    responses={200: RspListPluginSerializer()},
)
plugin_retrieve_docs = swagger_auto_schema(
    tags=plugin_tag,
    operation_id="插件管理-详情",
    responses={200: RspRetrievePluginSerializer()},
)
plugin_create_docs = swagger_auto_schema(
    tags=plugin_tag,
    operation_id="插件管理-添加",
    responses={200: RspCreatePluginSerializer()},
)
plugin_update_docs = swagger_auto_schema(
    tags=plugin_tag,
    request_body=ReqUpdatePluginSerializer,
    operation_id="插件管理-put",
    responses={200: BaseRspSerializer()},
)
plugin_delete_docs = swagger_auto_schema(
    tags=plugin_tag,
    operation_id="插件管理-删除",
    responses={200: BaseRspSerializer()},
)
