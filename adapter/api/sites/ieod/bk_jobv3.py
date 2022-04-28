from django.utils.translation import ugettext_lazy as _

from adapter.api.base import DataAPI
from adapter.sites.ieod.config.domains import JOB_APIGATEWAY_ROOT_V3


def get_job_request_before(params):
    """
    对请求参数进行处理
    """
    return params


class _JobV3Api:
    MODULE = _("JOB")

    @property
    def fast_execute_script(self):
        return DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "fast_execute_script",
            description=_("快速执行脚本"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def fast_transfer_file(self):
        return DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "fast_transfer_file",
            description=_("快速分发文件"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def get_job_instance_log(self):
        return DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_instance_log",
            description=_("根据作业ID获取执行日志"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def get_job_instance_ip_log(self):
        return DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_instance_ip_log",
            description=_("根据作业ID获取执行日志"),
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def get_job_instance_status(self):
        return DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_instance_status",
            description="根据作业实例 ID 查询作业执行状态",
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def get_job_plan_list(self):
        return DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_plan_list",
            description="查询执行方案列表",
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def get_job_plan_detail(self):
        return DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_plan_detail",
            description="查询执行方案详情",
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def get_job_instance_list(self):
        return DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_instance_list",
            description="查询作业实例列表(执行历史)",
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def get_job_instance_global_var_value(self):
        return DataAPI(
            method="GET",
            url=JOB_APIGATEWAY_ROOT_V3 + "get_job_instance_global_var_value",
            description="获取作业实例全局变量值",
            module=self.MODULE,
            before_request=get_job_request_before,
        )

    @property
    def operate_job_instance(self):
        return DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "operate_job_instance",
            description="作业实例操作",
            module=self.MODULE,
        )

    @property
    def operate_step_instance(self):
        return DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "operate_step_instance",
            description="步骤实例操作",
            module=self.MODULE,
        )

    @property
    def save_cron(self):
        return DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "save_cron",
            description="新建或保存定时作业",
            module=self.MODULE,
        )

    @property
    def update_cron_status(self):
        return DataAPI(
            method="POST",
            url=JOB_APIGATEWAY_ROOT_V3 + "update_cron_status",
            description="更新定时作业状态",
            module=self.MODULE,
        )


JobV3Api = _JobV3Api()
