# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from adapter.api.base import DataAPI
from adapter.sites.open.config.domains import SOPS_APIGATEWAY_ROOT_V2


def get_job_request_before(params):
    return params


class _SopsApi(object):
    MODULE = _("SOPS")

    def __init__(self):
        self.get_template_info = DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_template_info",
            description=_("查询单个模板详情"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_template_list = DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_template_list",
            description=_("查询模板列表"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_task_status = DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_task_status",
            description='查询任务或任务节点执行状态',
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_template_schemes_api = DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_template_schemes",
            description='查询任务或任务节点执行状态',
            module=self.MODULE,
            before_request=get_job_request_before,
        )


SopsApi = _SopsApi()
