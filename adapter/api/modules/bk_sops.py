from django.utils.translation import ugettext_lazy as _

from adapter.api.base import BaseApi, ProxyDataAPI


class _SopsApi(BaseApi):
    MODULE = _("SOPS")

    def __init__(self):
        self.get_task_status = ProxyDataAPI(_("查询任务或任务节点执行状态"))
        self.get_task_detail = ProxyDataAPI(_("查询任务执行详情"))
        self.get_template_info = ProxyDataAPI(_("查询单个模板详情"))
        self.preview_task_tree = ProxyDataAPI(_("预览模板创建后生成的任务树"))
        self.get_template_list = ProxyDataAPI(_("查询模板列表"))
        self.get_template_list_api = ProxyDataAPI(_("查询模板列表 网关"))
        self.get_template_schemes_api = ProxyDataAPI(_("获取模板的执行方案列表"))
        self.get_task_node_detail = ProxyDataAPI(_("获取执行节点"))
        self.operate_task = ProxyDataAPI(_("操作任务"))
        self.operate_node = ProxyDataAPI(_("操作节点"))
        self.node_callback = ProxyDataAPI(_("回调任务的节点"))
        self.get_task_list = ProxyDataAPI(_("获取任务列表"))
        self.get_tasks_status = ProxyDataAPI(_("批量获取任务状态"))
        self.get_user_project_list = ProxyDataAPI(_("获取用户有权限的项目列表"))


SopsApi = _SopsApi()
