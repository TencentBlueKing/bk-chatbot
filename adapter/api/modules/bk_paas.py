# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from adapter.api.base import DataAPI
from adapter.api.modules.utils import add_esb_info_before_request
from config.domains import BK_PAAS_APIGATEWAY_ROOT


class _BKPAASApi(object):
    MODULE = _("PaaS平台登录模块")

    def __init__(self):
        self.get_app_info = DataAPI(
            method="GET",
            url=BK_PAAS_APIGATEWAY_ROOT + "get_app_info/",
            module=self.MODULE,
            description="获取app信息",
            before_request=add_esb_info_before_request,
        )


BKPAASApi = _BKPAASApi()
