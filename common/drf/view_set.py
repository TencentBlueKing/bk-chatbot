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

from rest_framework import mixins, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ViewSet

from common.drf.pagination import DataPageNumberPagination


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # To not perform the csrf check previously happening
        return


class BaseViewSet(ViewSet):
    """
    没有额外的封装，直接使用
    """

    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    valida_response_data = False

    def serializer_response_data(self, data):
        """
        序列化返回
        """
        if not hasattr(self, f"{self.action}_valida"):
            return data
        serializer_class = getattr(self, f"{self.action}_serializer_class")
        serializer = serializer_class(data=data)
        if not serializer.is_valid():
            return data
        return serializer.data

    def finalize_response(self, request, response, *args, **kwargs):

        if not isinstance(response, Response):
            return response

        # 异常交给exception_handler来处理
        if response.exception:
            return super().finalize_response(request, response, *args, **kwargs)

        if response.data is None:
            response.data = {
                "result": True,
                "code": "200",
                "message": "success",
                "data": None,
            }
        if self.action in ["retrieve", "create", "update"] and response.data is not None:
            response.data = {
                "result": True,
                "code": "200",
                "message": "success",
                "data": response.data,
            }
        # 格式化响应
        response.data = self.serializer_response_data(response.data)
        # 返回响应头禁用浏览器的类型猜测行为
        response._headers["x-content-type-options"] = (
            "X-Content-Type-Options",
            "nosniff",
        )
        response.status_code = status.HTTP_200_OK
        return super().finalize_response(request, response, *args, **kwargs)


class NewBaseViewSet(BaseViewSet, GenericViewSet):
    """
    自定义一些属性
    """

    http_method_names = ["get", "post", "put", "delete"]  # 默认支持这4中,有需求可以重写

    def get_serializer_class(self):
        """
        序列化器使用
        @return:
        """
        if hasattr(self, f"{self.action}_serializer_class"):
            return getattr(self, f"{self.action}_serializer_class")
        return super().get_serializer_class()

    def _get_self_serializer_class(self):
        """
        返回自定义的序列化器
        """
        return getattr(self, f"{self.action}_serializer_class")

    def valida_serializer_class(self, data):
        serializer_class = getattr(self, f"{self.action}_serializer_class")
        serializer = serializer_class(data=data)
        return serializer


class BaseRetrieveViewSet(NewBaseViewSet, mixins.RetrieveModelMixin):
    pass


class BaseGetViewSet(NewBaseViewSet, mixins.ListModelMixin):
    """
    get请求
    """

    ordering = "-id"
    pagination_class = DataPageNumberPagination


class BaseCreateViewSet(NewBaseViewSet, mixins.CreateModelMixin):
    """
    添加
    """

    pass


class BaseUpdateViewSet(NewBaseViewSet, mixins.UpdateModelMixin):
    """
    更新
    """

    pass


class BaseDelViewSet(NewBaseViewSet, mixins.DestroyModelMixin):
    """
    删除
    """

    pass


class BaseManageViewSet(BaseGetViewSet, BaseCreateViewSet, BaseUpdateViewSet, BaseDelViewSet):
    pass


class BaseAllViewSet(BaseManageViewSet, BaseRetrieveViewSet):
    pass
