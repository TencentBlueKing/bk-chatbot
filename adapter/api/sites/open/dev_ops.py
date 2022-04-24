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

from adapter.api.base import DataAPI
from adapter.sites.open.config.domains import DEVOPS_APIGW


def set_headers(params: dict) -> dict:
    """
    把用户信息放在headers中
    """
    headers = {"X-DEVOPS-UID": params.get("bk_username", "")}
    return headers


def after_app_project_list(ret: dict) -> dict:
    """
    数据清理
    """

    ret["data"] = list(
        map(
            lambda x: {
                "bk_biz_id": x.get("project_code"),
                "name": x.get("project_name"),
                "project_id": x.get("project_id"),
            },
            ret.get("data", []),
        )
    )
    return ret


def after_app_pipeline_list(ret: dict) -> dict:
    """
    数据清理
    """

    ret["data"] = list(
        map(
            lambda x: {
                "bk_biz_id": x.get("projectId"),
                "id": x.get("pipelineId"),
                "name": x.get("pipelineName"),
            },
            ret.get("data", {}).get("records", []),
        )
    )
    return ret


def after_app_pipeline_start_info_list(ret: dict) -> dict:
    """
    数据清理
    """

    ret["data"] = ret.get("data", {}).get("properties", [])
    return ret

class _DevOpsApi:
    """
    使用蓝盾应用态的接口
    """

    MODULE = _("DEVOPS")

    @property
    def app_project_list(self):
        return DataAPI(
            method="GET",
            url=DEVOPS_APIGW + "projects/",
            description=_("应用态-获取项目列表"),
            module=self.MODULE,
            headers=set_headers,
            after_request=after_app_project_list,
            response_validation={"code": 0},
        )

    @property
    def app_pipeline_list(self):
        return DataAPI(
            method="GET",
            url=DEVOPS_APIGW + "projects/{projectId}/pipelines",
            description=_("应用态-获取项目的流水线列表"),
            module=self.MODULE,
            headers=set_headers,
            url_keys=["projectId"],
            after_request=after_app_pipeline_list,
            response_validation={"status": 0},
        )

    @property
    def app_build_start_info(self):
        return DataAPI(
            method="GET",
            url=DEVOPS_APIGW + "projects/{projectId}/pipelines/{pipelineId}/builds/manualStartupInfo",
            description=_("应用态-获取流水线启动参数"),
            module=self.MODULE,
            headers=set_headers,
            after_request=after_app_pipeline_start_info_list,
            url_keys=["projectId", "pipelineId"],
            response_validation={"status": 0},
        )

    @property
    def app_build_status(self):
        return DataAPI(
            method="GET",
            url=DEVOPS_APIGW + "projects/{projectId}/pipelines/{pipelineId}/builds/{buildId}/status",
            description=_("应用态-获取构建的状态信息"),
            module=self.MODULE,
            url_keys=["projectId", "pipelineId", "buildId"],
            headers=set_headers,
        )


DevOpsApi = _DevOpsApi()