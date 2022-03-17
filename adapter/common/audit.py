# -*- coding: utf-8 -*-
"""
自定义装饰器
"""
from rest_framework.response import Response
from rest_framework.request import Request

from blueapps.core.exceptions.base import BlueException
from adapter.common.exceptions import BaseException

# 审计日志装饰器


def record_audit_log(func):
    def wrapper(*args, **kwargs):

        # 请求参数
        audit_record_dict = {"method": "", "path": "", "created_by": "", "params": dict(), "operate_result": dict()}
        for _arg in args:
            if isinstance(_arg, Request):
                method = _arg.method
                audit_record_dict.update(
                    {
                        "method": method,
                        "path": _arg.path,
                        "created_by": _arg.user.username,
                        "params": _arg.query_params if method == "GET" else _arg.data,
                    }
                )
                break

        # 请求结果
        try:
            result = func(*args, **kwargs)

            # 非Response直接返回, 不记录日志
            if not isinstance(result, Response):
                return result

            audit_record_dict["operate_result"].update({"result": True, "data": result.data, "code": 0, "message": ""})
            return result
        except BaseException as e:
            audit_record_dict["operate_result"].update(
                {"code": e.code, "message": e.message, "data": e.data, "result": False}
            )
            raise e
        except BlueException as e:
            audit_record_dict["operate_result"].update(
                {"code": e.code, "message": e.MESSAGE, "data": "", "result": False}
            )
            raise e
        except Exception as e: # pylint: disable=broad-except
            audit_record_dict["operate_result"].update(
                {"code": 50000, "message": "系统异常,请联系管理员处理", "data": "", "result": False}
            )
            raise e

    return wrapper
