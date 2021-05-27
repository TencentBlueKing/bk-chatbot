# -*- coding: utf-8 -*-
import unicodedata
from html.parser import HTMLParser

from django.conf import settings


class APIModel(object):
    KEYS = []

    @classmethod
    def init_by_data(cls, data):
        kvs = {_key: data[_key] for _key in cls.KEYS}
        o = cls(**kvs)
        o._data = data
        return o

    def __init__(self, *args, **kwargs):
        self._data = None

    def _get_data(self):
        """
        获取基本数据方法，用于给子类重载
        """
        return None

    @property
    def data(self):
        if self._data is None:
            self._data = self._get_data()

        return self._data


def build_auth_args(request):
    """
    组装认证信息
    """
    # auth_args 用于ESB身份校验
    auth_args = {}
    if request is None:
        return auth_args

    for k, v in list(settings.OAUTH_COOKIES_PARAMS.items()):
        if v in request.COOKIES:
            auth_args.update({k: request.COOKIES[v]})

    return auth_args


def html_decode(key):
    """
    @summary:符号转义
    """
    h = HTMLParser()
    cleaned_text = unicodedata.normalize("NFKD", h.unescape(key).strip())
    return cleaned_text


def get_display_from_choices(key, choices):
    """
    choices中获取display
    @apiParam {List} flow_ids
    @apiParamExample {*args} 参数样例:
        "key": "project",
        "choices": (
            ("user", _("用户")),
            ("app", _("APP")),
            ("project", _("项目")),
    @apiSuccessExample {String}
        项目
    """
    for choice in choices:
        if key == choice[0]:
            return choice[1]
