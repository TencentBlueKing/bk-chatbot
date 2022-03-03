# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from adapter.api.base import DataAPI
from adapter.sites.open.config.domains import JOB_APIGATEWAY_ROOT_V3


def get_job_request_before(params):
    return params


class _JobV3Api(object):
    MODULE = _("JOB")

    def __init__(self):
        self.fast_execute_script = DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "fast_execute_script",
            description=_("快速执行脚本"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.fast_transfer_file = DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "fast_transfer_file",
            description=_("快速分发文件"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_job_instance_log = DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_instance_log",
            description=_("根据作业ID获取执行日志"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_job_instance_ip_log = DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_instance_ip_log",
            description=_("根据作业ID获取执行日志"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_job_instance_status = DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_instance_status",
            description='根据作业实例 ID 查询作业执行状态',
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_job_plan_list = DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_plan_list",
            description='查询执行方案列表',
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_job_plan_detail = DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_plan_detail",
            description='查询执行方案详情',
            module=self.MODULE,
            before_request=get_job_request_before,
        )
        self.get_job_instance_list = DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_instance_list",
            description='查询作业实例列表(执行历史)',
            module=self.MODULE,
            before_request=get_job_request_before,
        )


JobV3Api = _JobV3Api()
