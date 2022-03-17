# -*- coding: utf-8 -*-

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

import datetime
import json
from functools import wraps

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.db import connection, transaction
from django.http import Http404
from django.utils.decorators import classonlymethod
from django.utils.translation import ugettext as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, filters, serializers, status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import ModelViewSet as _ModelViewSet
from rest_framework.viewsets import ViewSet

from blueapps.utils.logger import logger
from common.exceptions import BaseException, ErrorCode, RouteDisabledError, ValidationError


def login_exempt(view_func):
    """ "Mark a view function as being exempt from login view protection"""

    def wrapped_view(*args, **kwargs):
        for arg in args:
            if isinstance(arg, WSGIRequest):
                arg.login_exempt = True
        return view_func(*args, **kwargs)

    wrapped_view.login_exempt = True
    return wraps(view_func)(wrapped_view)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # To not perform the csrf check previously happening
        return


class CreateMixin:
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["created_by"] = request.user.username
        data["created_at"] = datetime.datetime.now()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UpdateMixin:
    def update(self, request, *args, **kwargs):
        data = request.data.copy()
        data["updated_by"] = request.user.username
        data["updated_at"] = datetime.datetime.now()
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class DestroyMixin:
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = datetime.datetime.now()
        instance.deleted_by = request.user.username
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResponseMixin:
    """
    统一接口返回格式
    """

    authentication_classes = (
        CsrfExemptSessionAuthentication,
        BasicAuthentication,
    )

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
        else:
            response.data = {
                "result": True,
                "code": "200",
                "message": "success",
                "data": response.data,
            }

        # 返回响应头禁用浏览器的类型猜测行为
        response._headers["x-content-type-options"] = (
            "X-Content-Type-Options",
            "nosniff",
        )
        response.status_code = status.HTTP_200_OK

        return super().finalize_response(request, response, *args, **kwargs)

    def valid(self, form_class, filter_blank=False, filter_none=False):
        """
        校验参数是否满足组 form_class 的校验
        @param {django.form.Form} form_class 验证表单
        @param {Boolean} filter_blank 是否过滤空字符的参数
        @param {Boolean} filter_none 是否过滤 None 的参数

        @raise FormError 表单验证不通过时抛出
        """
        if self.request.method == "GET":
            _form = form_class(self.request.query_params)
        else:
            _form = form_class(self.request.data)

        if not _form.is_valid():
            raise ValidationError(_form.format_errmsg())
        _data = _form.cleaned_data
        if filter_blank:
            _data = {_k: _v for _k, _v in list(_data.items()) if _v != ""}
        if filter_none:
            _data = {
                _k: _v
                for _k, _v in list(
                    _data.items(),
                )
                if _v is not None
            }

        return _data

    def valid_serializer(self, serializer):
        """
        校验参数是否满足组 serializer 的校验
        @param {serializer} serializer 验证表单
        @return {serializer} _serializer 序列器（已进行校验清洗）
        """
        _request = self.request
        if _request.method == "GET":
            _serializer = serializer(data=_request.query_params)
        else:
            _serializer = serializer(data=_request.data)
        _serializer.is_valid(raise_exception=True)
        return _serializer

    def is_pagination(self, request):
        page = request.query_params.get("page", "")
        page_size = request.query_params.get("page_size", "")
        return page != "" and page_size != ""

    def do_paging(self, request, data):
        # 处理分页
        if self.is_pagination(request):
            page = int(request.query_params["page"])
            page_size = int(request.query_params["page_size"])

            count = len(data)
            total_page = (count + page_size - 1) / page_size
            data = data[page_size * (page - 1) : page_size * page]

            return {"total_page": total_page, "count": count, "data": data}
        else:
            # 无分页请求时返回全部
            return {"total_page": 1, "count": len(data), "data": data}


class ApiGatewayMixin(ResponseMixin):
    """
    API网关接口取消认证
    """

    authentication_classes = ()


class ValidationMixin:
    def params_valid(self, serializer, params=None, context=None) -> dict:
        """
        校验参数是否满足 serializer 规定的格式
        """
        # 获得Django的request对象
        current_request = self.request

        # 校验request中的参数
        if not params:
            if current_request.method in ["GET"]:
                params = current_request.query_params
            else:
                params = current_request.data

        return valid_params(serializer_class=serializer, params=params, context=context)


class DataPageNumberPagination(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "pagesize"
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response(data)


class BaseViewSet(ViewSet):
    authentication_classes = (
        CsrfExemptSessionAuthentication,
        BasicAuthentication,
    )

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
        else:
            response.data = {
                "result": True,
                "code": "200",
                "message": "success",
                "data": response.data,
            }

        # 返回响应头禁用浏览器的类型猜测行为
        response._headers["x-content-type-options"] = ("X-Content-Type-Options", "nosniff")
        response.status_code = status.HTTP_200_OK

        return super().finalize_response(request, response, *args, **kwargs)


class APIViewSet(ResponseMixin, ValidationMixin, GenericViewSet):
    @classonlymethod
    def as_login_exempt_view(cls, *args, **kwargs):
        return login_exempt(cls.as_view(*args, **kwargs))


class Meta:
    pass


class APIModelViewSet(ResponseMixin, _ModelViewSet):
    model = None
    pagination_class = DataPageNumberPagination
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    SearchFilterserializer_meta = type("Meta", (Meta,), {"model": None})

    DISABLE_ROUTES = []

    def create(self, request, *args, **kwargs):
        if "create" in self.DISABLE_ROUTES:
            raise RouteDisabledError()
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if "list" in self.DISABLE_ROUTES:
            raise RouteDisabledError()
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if "retrieve" in self.DISABLE_ROUTES:
            raise RouteDisabledError()
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if "update" in self.DISABLE_ROUTES:
            raise RouteDisabledError()
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if "destroy" in self.DISABLE_ROUTES:
            raise RouteDisabledError()
        return super().destroy(request, *args, **kwargs)

    @property
    def validated_data(self):
        if self.request.method == "GET":
            data = self.request.query_params
        else:
            data = self.request.data
        serializer = self.get_serializer_class()(data=data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    @classonlymethod
    def as_login_exempt_view(cls, *args, **kwargs):

        return login_exempt(cls.as_view(*args, **kwargs))


class DataSerializerMixin:
    """
    该 Mixin 类主要用于重载部分 Serializer 方法
    """

    def is_valid(self, raise_exception=False):
        if not raise_exception:
            return super().is_valid()

        try:
            return super().is_valid(raise_exception=True)
        except exceptions.ValidationError as exc:
            # 对于DRF默认返回的校验异常，需要额外补充 message 字段
            # 由于 ValidationError 需要返回给前端，需要把错误信息处理一下
            exc.message = self.format_errmsg()
            raise exc

    def format_errmsg(self):
        """
        格式化 DRF serializer 序列化器返回错误信息，简化为字符串提示，错误信息形如：
            {
                "result_tables": {
                    "non_field_errors": [
                        "结果表不可为空"
                    ]
                },
                "app_code": [
                    "该字段是必填项。"
                ]
            }
        @return {String} 简化后的提示信息
        @returnExample
            结果表，结果表不可为空
        """
        errors = self.errors
        declared_fields = self.fields

        _key, _val = list(errors.items())[0]
        _whole_key = _key

        while type(_val) is dict:
            _key, _val = list(_val.items())[0]
            _whole_key += "." + _key

        _key_display = ""
        for _key in _whole_key.split("."):
            # 特殊KEY，表示全局字段
            if _key == "non_field_errors":
                break

            _field = declared_fields[_key]
            if hasattr(_field, "child"):
                declared_fields = _field.child

            _key_display = _field.label if _field.label else _key

        format_msg = f"{_key_display}，{_val[0]}"
        return format_msg


class DataSerializer(DataSerializerMixin, serializers.Serializer):
    pass


class DataModelSerializer(DataSerializerMixin, serializers.ModelSerializer):
    pass


def valid_params(serializer_class, params, context=None):
    """利用序列化器来校验参数，返回合法数据"""
    serializer = serializer_class(
        data=params,
        context=context or {},
        many=False,
    )

    try:
        serializer.is_valid(raise_exception=True)
    except serializers.ValidationError:
        try:
            message = format_serializer_errors(
                serializer.errors,
                serializer.fields,
                params,
            )
        except Exception: # pylint: disable=broad-except
            message = f"参数校验失败: {serializer.errors}"

        raise serializers.ValidationError(message)

    return serializer.validated_data


def format_validation_message(e):
    """格式化drf校验错误信息"""

    if isinstance(e.detail, list):
        message = "; ".join([f"{k}:{v}" for k, v in enumerate(e.detail)])
    elif isinstance(e.detail, dict):
        messages = []
        for k, v in e.detail.items():
            if isinstance(v, list):
                try:
                    messages.append("{}:{}".format(k, ",".join(v)))
                except TypeError:
                    messages.append("{}:{}".format(k, "部分列表元素的参数不合法，请检查"))
            else:
                messages.append(f"{k}:{v}")
        message = ";".join(messages)
    else:
        message = e.detail

    return message


def format_serializer_errors(errors, fields, params, prefix="  "):
    # 若只返回其中一条校验错误的信息，则只需要把注释的三个return打开即可
    message = "参数校验失败:\n" if prefix == "  " else "\n"
    for key, field_errors in errors.items():
        sub_message = ""
        label = key
        if key not in fields:
            sub_message = json.dumps(field_errors)
        else:
            field = fields[key]
            label = field.label or field.field_name
            if (
                hasattr(field, "child")
                and isinstance(field_errors, list)
                and len(field_errors) > 0
                and not isinstance(field_errors[0], str)
            ):
                for index, sub_errors in enumerate(field_errors):
                    if sub_errors:
                        sub_format = format_serializer_errors(
                            sub_errors,
                            field.child.fields,
                            params,
                            prefix=prefix + "    ",
                        )
                        # return sub_format
                        sub_message += "\n{prefix}第{index}项:".format(
                            prefix=prefix + "  ",
                            index=index + 1,
                        )
                        sub_message += sub_format
            else:
                if isinstance(field_errors, dict):
                    if hasattr(field, "child"):
                        sub_foramt = format_serializer_errors(
                            field_errors,
                            field.child.fields,
                            params,
                            prefix=prefix + "  ",
                        )
                    else:
                        sub_foramt = format_serializer_errors(
                            field_errors,
                            field.fields,
                            params,
                            prefix=prefix + "  ",
                        )
                    # return sub_foramt
                    sub_message += sub_foramt
                elif isinstance(field_errors, list):
                    for index, __ in enumerate(field_errors):
                        field_errors[index] = field_errors[index].format(
                            **{key: params.get(key, "")},
                        )
                        # return field_errors[index]
                        sub_message += "{index}.{error}".format(
                            index=index + 1,
                            error=field_errors[index],
                        )
                    sub_message += "\n"
        message += "{prefix}{label}: {message}".format(
            prefix=prefix,
            label=label,
            message=sub_message,
        )
    return message


def format_error_response(code=None, message="", data=None, errors=None):
    if len(str(code)) == 3:
        code = ErrorCode.SYS_PLAT_CODE + ErrorCode.SYS_WEB_CODE + code
    message = message + "(" + code + ")"
    return {
        "result": False,
        "code": code,
        "data": data,
        "message": message,
        "errors": errors,
    }


def set_rollback():
    atomic_requests = connection.settings_dict.get("ATOMIC_REQUESTS", False)
    if atomic_requests and connection.in_atomic_block:
        transaction.set_rollback(True)


def custom_exception_handler(exc, context):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException`, and also
    Django's built-in `Http404` and `PermissionDenied` exceptions.

    Any unhandled exceptions may return `None`, which will cause a 500 error
    to be raised.
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    # ValidationError is subclass of APIException
    if isinstance(exc, exceptions.APIException):
        data = format_error_response(
            "{}".format(
                exc.status_code,
            ),
            format_validation_message(exc),
        )
        set_rollback()
        return Response(data)

    if isinstance(exc, BaseException):
        logger.error(
            "API_FAIL: {message}, code={code}, args={args}".format(
                message=exc.message,
                code=exc.code,
                args=exc.args,
            ),
        )
        data = format_error_response(
            exc.code,
            exc.message,
            exc.data,
            exc.errors,
        )
        set_rollback()
        return Response(data)

    error_message = _("系统错误，请联系管理员")
    if settings.DEBUG:
        error_message += f": {str(exc)}"
    logger.exception(f"API_ERROR: {str(exc)}")
    return Response(format_error_response("500", error_message))
