# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from adapter.api.base import BaseApi, ProxyDataAPI


class _SopsApi(BaseApi):
    MODULE = _("SOPS")

    def __init__(self):
        self.get_task_status = ProxyDataAPI(_("查询任务或任务节点执行状态"))
        self.get_template_info = ProxyDataAPI(_("查询单个模板详情"))
        self.get_template_list = ProxyDataAPI(_("查询模板列表"))
        self.get_template_list_api = ProxyDataAPI(_("查询模板列表 网关"))
        self.get_template_schemes_api = ProxyDataAPI(_("获取模板的执行方案列表"))


SopsApi = _SopsApi()
