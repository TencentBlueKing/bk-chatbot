from django.utils.translation import ugettext_lazy as _

from adapter.api.base import BaseApi, ProxyDataAPI


class _JobV3Api(BaseApi):
    MODULE = _("JOBV3")

    def __init__(self):
        self.fast_execute_script = ProxyDataAPI(_("快速执行脚本"))
        self.fast_transfer_file = ProxyDataAPI(_("快速分发文件"))
        self.get_task_ip_log = ProxyDataAPI(_("获取任务执行记录"))
        self.get_job_instance_log = ProxyDataAPI(_("根据作业ID获取作业执行记录"))
        self.get_job_instance_global_var_value = ProxyDataAPI(_("获取作业实例全局变量值"))
        self.get_job_instance_ip_log = ProxyDataAPI(_("根据作业ID查询作业执行日志"))
        self.get_job_instance_status = ProxyDataAPI(_("根据作业ID查询作业执行状态"))
        self.get_job_plan_list = ProxyDataAPI(_("查询执行方案列表"))
        self.get_job_plan_detail = ProxyDataAPI(_("查询执行方案详情"))
        self.get_job_instance_list = ProxyDataAPI(_("查询作业实例列表(执行历史)"))
        self.operate_job_instance = ProxyDataAPI(_("作业实例操作"))
        self.operate_step_instance = ProxyDataAPI(_("步骤实例操作"))
        self.save_cron = ProxyDataAPI(_("新建或保存定时作业"))
        self.update_cron_status = ProxyDataAPI(_("更新定时作业状态，如启动或暂停"))


JobV3Api = _JobV3Api()
