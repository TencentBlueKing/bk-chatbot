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

from django.utils.translation import ugettext_lazy as _

from adapter.api.base import BaseApi, ProxyDataAPI


class _JobV3Api(BaseApi):
    MODULE = _("JOBV3")

    def __init__(self):
        self.fast_execute_script = ProxyDataAPI(_("快速执行脚本"))
        self.fast_transfer_file = ProxyDataAPI(_("快速分发文件"))
        self.get_task_ip_log = ProxyDataAPI(_("获取任务执行记录"))
        self.get_job_instance_log = ProxyDataAPI(_("根据作业ID获取作业执行记录"))
        self.get_job_instance_ip_log = ProxyDataAPI(_("根据作业ID查询作业执行日志"))
        self.get_job_instance_status = ProxyDataAPI(_("根据作业ID查询作业执行状态"))
        self.get_job_plan_list = ProxyDataAPI(_("查询执行方案列表"))
        self.get_job_plan_detail = ProxyDataAPI(_("查询执行方案详情"))
        self.get_job_instance_list = ProxyDataAPI(_("查询作业实例列表(执行历史)"))


JobV3Api = _JobV3Api()
