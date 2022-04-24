# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from adapter.api.base import ProxyDataAPI, BaseApi


class _BkLogApi(BaseApi):
    MODULE = _("log_search元数据")

    def __init__(self):
        self.search = ProxyDataAPI("查询数据")
        self.mapping = ProxyDataAPI("拉取索引mapping")
        self.dsl = ProxyDataAPI("查询数据DSL模式")
        self.scroll = ProxyDataAPI("scroll滚动查询")
        self.indices = ProxyDataAPI("获取集群信息")
        self.cluster = ProxyDataAPI("获取集群信息")


BkLog = _BkLogApi()
