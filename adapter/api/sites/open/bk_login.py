# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from adapter.api.base import DataAPI
from adapter.api.modules.utils import add_esb_info_before_request
from config.domains import BK_LOGIN_APIGATEWAY_ROOT


class _BKLoginApi(object):
    MODULE = _("PaaS平台登录模块")

    def __init__(self):
        self.get_all_user = DataAPI(
            method="POST",
            url=BK_LOGIN_APIGATEWAY_ROOT + "get_all_user/",
            module=self.MODULE,
            description="获取所有用户",
            before_request=add_esb_info_before_request,
            cache_time=300,
        )
        self.get_user = DataAPI(
            method="POST",
            url=BK_LOGIN_APIGATEWAY_ROOT + "get_user/",
            module=self.MODULE,
            description="获取单个用户",
            before_request=add_esb_info_before_request,
        )


BKLoginApi = _BKLoginApi()
