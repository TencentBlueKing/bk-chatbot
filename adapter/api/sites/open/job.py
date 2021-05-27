# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from adapter.api.base import DataAPI
from adapter.sites.open.config.domains import JOB_APIGATEWAY_ROOT_V2


def get_job_request_before(params):
    return params


class _JobApi(object):
    MODULE = _("JOB")

    def __init__(self):
        self.fast_execute_script = DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V2 + "fast_execute_script",
            description=_("快速执行脚本"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.fast_push_file = DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V2 + "fast_push_file",
            description=_("快速分发文件"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_job_instance_log = DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V2 + "get_job_instance_log",
            description=_("根据作业ID获取执行日志"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_job_list = DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V2 + "get_job_list",
            description=' 查询作业执行方案列表',
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_job_detail = DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V2 + "get_job_detail",
            description='查询执行方案详情',
            module=self.MODULE,
            before_request=get_job_request_before,
        )

JobApi = _JobApi()
