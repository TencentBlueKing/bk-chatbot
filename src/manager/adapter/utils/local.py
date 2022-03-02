# -*- coding: utf-8 -*-
"""
记录线程变量
"""
import uuid
import sys
from threading import local

from blueapps.utils import get_request

_local = local()


def activate_request(request, request_id=None):
    """
    激活request线程变量
    """
    if not request_id:
        request_id = str(uuid.uuid4())
    request.request_id = request_id
    _local.request = request
    return request


def get_request_id():
    """
    获取request_id
    """
    try:
        return get_request().request_id
    except Exception: # pylint: disable=broad-except
        return str(uuid.uuid4())


def get_request_username():
    """
    获取请求的用户名
    """
    username = ""
    try:
        username = get_request().user.username
    except Exception: # pylint: disable=broad-except
        pass
    finally:
        if not username and "celery" in sys.argv:
            username = "admin"
    return username
