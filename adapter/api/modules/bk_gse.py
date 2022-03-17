# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from adapter.api.base import BaseApi, ProxyDataAPI


class _GseApi(BaseApi):
    MODULE = _("GSE")

    def __init__(self):
        self.get_agent_status = ProxyDataAPI("获取agent状态")


GseApi = _GseApi()
