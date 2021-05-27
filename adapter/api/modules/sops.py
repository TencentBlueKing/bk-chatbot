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


class _SopsApi(BaseApi):
    MODULE = _("SOPS")

    def __init__(self):
        self.get_task_status = ProxyDataAPI(_("查询任务或任务节点执行状态"))
        self.get_template_info = ProxyDataAPI(_("查询单个模板详情"))
        self.get_template_list = ProxyDataAPI(_("查询模板列表"))
        self.get_template_list_api = ProxyDataAPI(_("查询模板列表 网关"))
        self.get_template_schemes_api = ProxyDataAPI(_("获取模板的执行方案列表"))


SopsApi = _SopsApi()
