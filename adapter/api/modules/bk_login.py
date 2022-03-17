# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from ..base import ProxyDataAPI, BaseApi


class _BKLoginApi(BaseApi):
    MODULE = _("PaaS平台登录模块")

    def __init__(self):
        self.get_all_user = ProxyDataAPI("获取单个用户")
        self.get_user = ProxyDataAPI("获取所有用户")


BKLoginApi = _BKLoginApi()
