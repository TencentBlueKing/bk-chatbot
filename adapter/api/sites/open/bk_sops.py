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

    @property
    def get_task_node_detail(self):
        """
        查询任务节点执行详情
        """
        return DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_task_node_detail/{task_id}/{bk_biz_id}/",
            description="查询任务节点执行详情",
            url_keys=["task_id", "bk_biz_id"],
            module=self.MODULE,
        )

    @property
    def operate_task(self):
        return DataAPI(
            method="POST",
            url=SOPS_APIGATEWAY_ROOT_V2 + "operate_task/{task_id}/{bk_biz_id}/",
            description="操作任务",
            url_keys=["task_id", "bk_biz_id"],
            module=self.MODULE,
        )

    @property
    def operate_node(self):
        return DataAPI(
            method="POST",
            url=SOPS_APIGATEWAY_ROOT_V2 + "operate_node/{bk_biz_id}/{task_id}/",
            description="查询任务节点执行详情",
            url_keys=["task_id", "bk_biz_id"],
            module=self.MODULE,
        )

    @property
    def node_callback(self):
        return DataAPI(
            method="POST",
            url=SOPS_APIGATEWAY_ROOT_V2 + "node_callback/{task_id}/{bk_biz_id}/",
            description="回调任务的节点",
            url_keys=["task_id", "bk_biz_id"],
            module=self.MODULE,
        )

    @property
    def get_task_list(self):
        return DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_task_list/{bk_biz_id}/",
            description="获取任务列表",
            url_keys=["bk_biz_id"],
            module=self.MODULE,
        )

    @property
    def get_tasks_status(self):
        return DataAPI(
            method="POST",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_tasks_status/{bk_biz_id}/",
            description="批量查询任务状态",
            url_keys=["bk_biz_id"],
            module=self.MODULE,
        )

    @property
    def get_user_project_list(self):
        return DataAPI(
            method="GET",
            url=SOPS_APIGATEWAY_ROOT_V2 + "get_user_project_list/",
            description="获取用户有权限的项目列表",
            module=self.MODULE,
        )


SopsApi = _SopsApi()
