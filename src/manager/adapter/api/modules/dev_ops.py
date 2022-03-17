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


class _DevOpsApi(BaseApi):
    MODULE = _("DEVOPS")

    def __init__(self):
        self.app_project_list = ProxyDataAPI(_("应用态-获取项目列表"))
        self.app_pipeline_list = ProxyDataAPI(_("应用态-获取项目的流水线列表"))
        self.app_pipeline_get = ProxyDataAPI(_("应用态-获取流水线编排"))
        self.app_build_start_info = ProxyDataAPI(_("应用态-获取流水线启动参数"))
        self.app_build_status = ProxyDataAPI(_("应用态-获取构建的状态信息"))
        self.app_build_detail = ProxyDataAPI(_("应用态-获取流水线构建详情"))
        self.app_build_stop = ProxyDataAPI(_("应用态-停止流水线"))
        self.app_build_retry = ProxyDataAPI(_("应用态-重试流水线"))


DevOpsApi = _DevOpsApi()
