# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云PaaS平台社区版 (BlueKing PaaSCommunity Edition) available.
Copyright (C) 2017-2018 THL A29 Limited,
a Tencent company. All rights reserved.
Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from ..base import ComponentAPI


class CollectionsJOBV3(object):
    """Collections of JOBV3 APIS"""

    def __init__(self, client):
        self.client = client

        self.execute_job_plan = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/jobv3/execute_job_plan/',
            description='执行作业执行方案',
        )
        self.fast_execute_script = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/jobv3/fast_execute_script/',
            description='快速执行脚本',
        )
        self.fast_execute_sql = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/jobv3/fast_execute_sql/',
            description='快速执行SQL',
        )
        self.fast_transfer_file = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/jobv3/fast_transfer_file/',
            description='快速分发文件',
        )
        self.get_account_list = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_account_list/',
            description='查询业务下的执行账号',
        )
        self.get_cron_detail = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_cron_detail/',
            description='查询定时作业详情',
        )
        self.get_cron_list = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_cron_list/',
            description='查询业务下定时作业信息',
        )
        self.get_job_instance_global_var_value = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_job_instance_global_var_value/',
            description='获取作业实例全局变量值',
        )
        self.get_job_instance_ip_log = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_job_instance_ip_log/',
            description='根据作业实例ID查询作业执行日志',
        )
        self.get_job_instance_list = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_job_instance_list/',
            description='查询作业实例列表(执行历史)',
        )
        self.get_job_instance_status = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_job_instance_status/',
            description='根据作业实例 ID 查询作业执行状态',
        )
        self.get_job_plan_detail = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_job_plan_detail/',
            description='查询执行方案详情',
        )
        self.get_job_plan_list = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_job_plan_list/',
            description='查询执行方案列表',
        )
        self.get_job_template_list = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_job_template_list/',
            description='查询作业模版列表',
        )
        self.get_public_script_list = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_public_script_list/',
            description='查询公共脚本列表',
        )
        self.get_public_script_version_detail = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_public_script_version_detail/',
            description='查询公共脚本详情',
        )
        self.get_public_script_version_list = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_public_script_version_list/',
            description='查询公共脚本版本列表',
        )
        self.get_script_list = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_script_list/',
            description='查询脚本列表',
        )
        self.get_script_version_detail = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_script_version_detail/',
            description='查询脚本详情',
        )
        self.get_script_version_list = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/jobv3/get_script_version_list/',
            description='查询脚本版本列表',
        )
        self.operate_job_instance = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/jobv3/operate_job_instance/',
            description='作业实例操作',
        )
        self.operate_step_instance = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/jobv3/operate_step_instance/',
            description='步骤实例操作',
        )
        self.save_cron = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/jobv3/save_cron/',
            description='新建或保存定时作业',
        )
        self.update_cron_status = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/jobv3/update_cron_status/',
            description='更新定时作业状态，如启动或暂停',
        )
