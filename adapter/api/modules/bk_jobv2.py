# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from adapter.api.base import BaseApi, ProxyDataAPI


class _JobV2Api(BaseApi):
    MODULE = _("JOB_V2")

    def __init__(self):
        self.fast_execute_script = ProxyDataAPI(_("快速执行脚本"))
        self.fast_push_file = ProxyDataAPI(_("快速分发文件"))
        self.get_task_ip_log = ProxyDataAPI(_("获取任务执行记录"))
        self.get_job_instance_log = ProxyDataAPI(_("根据作业ID获取作业执行记录"))
        self.get_job_list = ProxyDataAPI(_("查询作业执行方案列表"))
        self.get_job_detail = ProxyDataAPI(_("查询执行方案详情"))


JobV2Api = _JobV2Api()
