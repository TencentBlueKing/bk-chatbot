# -*- coding: utf-8 -*-
from ..base import ComponentAPI


class CollectionsSOPS(object):
    """Collections of SOPS APIS"""

    def __init__(self, client):
        self.client = client

        self.create_periodic_task = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/sops/create_periodic_task/',
            description='通过流程模板新建周期任务',
        )
        self.create_task = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/sops/create_task/',
            description='通过流程模板新建任务',
        )
        self.get_periodic_task_info = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/sops/get_periodic_task_info/',
            description='查询业务下的某个周期任务详情',
        )
        self.get_periodic_task_list = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/sops/get_periodic_task_list/',
            description='查询业务下的周期任务列表',
        )
        self.get_task_detail = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/sops/get_task_detail/',
            description='查询任务执行详情',
        )
        self.get_task_node_detail = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/sops/get_task_node_detail/',
            description='查询任务节点执行详情',
        )
        self.get_task_status = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/sops/get_task_status/',
            description='查询任务或任务节点执行状态',
        )
        self.get_template_info = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/sops/get_template_info/',
            description='查询单个模板详情',
        )
        self.get_template_list = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/sops/get_template_list/',
            description='查询模板列表',
        )
        self.import_common_template = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/sops/import_common_template/',
            description='导入公共流程',
        )
        self.modify_constants_for_periodic_task = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/sops/modify_constants_for_periodic_task/',
            description='修改周期任务的全局参数',
        )
        self.modify_cron_for_periodic_task = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/sops/modify_cron_for_periodic_task/',
            description='修改周期任务的调度策略',
        )
        self.node_callback = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/sops/node_callback/',
            description='回调任务节点',
        )
        self.operate_task = ComponentAPI(
            client=self.client, method='POST', path='/api/c/compapi{bk_api_ver}/sops/operate_task/', description='操作任务'
        )
        self.query_task_count = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/sops/query_task_count/',
            description='查询任务分类统计总数',
        )
        self.set_periodic_task_enabled = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/sops/set_periodic_task_enabled/',
            description='设置周期任务是否激活',
        )
        self.start_task = ComponentAPI(
            client=self.client, method='POST', path='/api/c/compapi{bk_api_ver}/sops/start_task/', description='开始执行任务'
        )
