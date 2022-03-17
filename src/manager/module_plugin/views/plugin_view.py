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
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework.decorators import action

from common.drf.view_set import BaseAllViewSet
from src.manager.module_plugin.hanlder.deal_plugin_count import get_plugin_exec
from src.manager.module_plugin.hanlder.deal_plugin_status import DealPluginStatus, del_stag_plugin
from src.manager.module_plugin.models import Plugin
from src.manager.module_plugin.proto.plugin import (
    PluginSerializer,
    ReqListPluginSerializer,
    ReqUpdatePluginSerializer,
    plugin_create_docs,
    plugin_delete_docs,
    plugin_list_docs,
    plugin_private_docs,
    plugin_retrieve_docs,
    plugin_update_docs,
)


@method_decorator(name="private", decorator=plugin_private_docs)
@method_decorator(name="list", decorator=plugin_list_docs)
@method_decorator(name="retrieve", decorator=plugin_retrieve_docs)
@method_decorator(name="create", decorator=plugin_create_docs)
@method_decorator(name="update", decorator=plugin_update_docs)
@method_decorator(name="destroy", decorator=plugin_delete_docs)
class PluginViewSet(BaseAllViewSet):
    """
    视图函数
    """

    queryset = Plugin.objects.all()
    serializer_class = PluginSerializer
    list_serializer_class = ReqListPluginSerializer
    update_serializer_class = ReqUpdatePluginSerializer
    private_serializer_class = ReqListPluginSerializer
    filterset_class = Plugin.OpenApiFilter

    def list(self, request, *args, **kwargs):
        request.query_params._mutable = True
        biz_id = self.request.payload.get("biz_id", None)
        if biz_id:
            request.query_params["biz_list"] = f'"{self.request.payload.get("biz_id")}"'
        exec_count_ret = get_plugin_exec()
        data = super().list(self, request, *args, **kwargs)
        obj_list = data.data.get("data")
        for obj in obj_list:
            obj["plugin_exec_count"] = exec_count_ret.get(obj.get("plugin_key"), 0)
        return data

    def perform_update(self, serializer):
        """
        @param serializer:
        @return:
        """
        with transaction.atomic():
            instance = serializer.instance
            # 老状态
            old_status = instance.plugin_status
            serializer.save()  # 保存数据的时候替换instance里面的数据
            new_status = instance.plugin_status
            username = self.request.user.username
            if username not in instance.developers:
                raise PermissionError("not have permission to update plugin")

            # 状态流转
            if new_status == Plugin.PluginStatus.STAG.value or new_status != old_status:
                # 处理逻辑
                DealPluginStatus.do(instance, new_status, old_status)

    def perform_destroy(self, instance: Plugin):
        """
        删除之前先判断是否已经下架
        :param instance:
        :return:
        """

        # 权限认证
        username = self.request.user.username
        if username not in instance.developers:
            raise PermissionError("not have permission to delete plugin")

        plugin_status = [Plugin.PluginStatus.DEFAULT.value, Plugin.PluginStatus.STAG.value]
        if instance.plugin_status in plugin_status:
            del_stag_plugin(instance)
            instance.delete()
        else:
            raise Exception("插件只有在能刚添加状态和下线状态能进行删除")

    @action(detail=False, methods=["GET"])
    def private(self, request, *args, **kwargs):
        request.query_params._mutable = True
        request.query_params["developers"] = f'"{self.request.user.username}"'
        return super().list(self, request, *args, **kwargs)
