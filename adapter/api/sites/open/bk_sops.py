# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from adapter.api.base import DataAPI
from adapter.sites.open.config.domains import SOPS_APIGATEWAY_ROOT_V2


def get_job_request_before(params):
    return params


class _SopsApi(object):
    MODULE = _("SOPS")

    @property
    def get_template_info(self):
        return DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_template_info",
            description=_("查询单个模板详情"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def preview_task_tree(self):
        return DataAPI(
            method="POST",
            url=SOPS_APIGATEWAY_ROOT_V2 + "/preview_task_tree/{bk_biz_id}/{template_id}/",
            description="预览模板创建后生成的任务树",
            url_keys=["bk_biz_id", "template_id"],
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def get_template_list(self):
        return DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_template_list",
            description=_("查询模板列表"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def get_task_status(self):
        return DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_task_status",
            description="查询任务或任务节点执行状态",
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def get_template_schemes_api(self):
        return DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_template_schemes",
            description="查询任务或任务节点执行状态",
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def get_task_detail(self):
        return DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_task_detail",
            description="查询任务节点执行详情",
            module=self.MODULE,
        )


SopsApi = _SopsApi()
