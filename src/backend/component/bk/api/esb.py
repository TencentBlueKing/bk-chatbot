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

from typing import Any, Dict, List

from component.bk.api.base import BKApi


class CC:
    """
    CC api shortcut
    """

    def __init__(self, bk_cc_api: BKApi):
        self.bk_cc_api = bk_cc_api

    async def search_business(self, **params) -> Dict:
        """
        -params:
        bk_username
        """
        return await self.bk_cc_api.call_action('search_business/', 'POST', json=params)


class JOB:
    """
    JOB api shortcut
    """

    def __init__(self, bk_job_api: BKApi):
        self.bk_job_api = bk_job_api

    async def execute_job_plan(self, **params) -> Any:
        """
        -params:
        bk_biz_id
        job_plan_id
        global_var_list
        bk_supplier_account
        bk_username
        """
        return await self.bk_job_api.call_action('execute_job_plan/', 'POST', json=params)

    async def get_job_plan_list(self, **params) -> Any:
        """
        -params:
        bk_biz_id long
        """
        return await self.bk_job_api.call_action('get_job_plan_list/', 'GET', params=params)

    async def get_job_plan_detail(self, **params) -> Any:
        """
        -params:
        bk_biz_id long
        job_plan_id long
        """
        return await self.bk_job_api.call_action('get_job_plan_detail/', 'GET', params=params)


class SOPS:
    """
    sops api shortcut
    """

    def __init__(self, bk_sops_api: BKApi):
        self.bk_sops_api = bk_sops_api

    async def get_template_info(self, bk_biz_id, template_id, **params) -> Dict:
        """
        -params:
        template_id
        bk_biz_id
        """
        return await self.bk_sops_api.call_action(f'get_template_info/{template_id}/{bk_biz_id}/',
                                                'GET', params=params)

    async def create_task(self, **params) -> Dict:
        """
        -params:
        template_id
        bk_biz_id
        -body
        constants
        exclude_task_nodes_id
        name
        bk_supplier_account
        bk_username
        """
        return await self.bk_sops_api.call_action(f'create_task/', 'POST', json=params)

    async def start_task(self, **params) -> Dict:
        """
        -params:
        task_id
        bk_biz_id
        -body
        bk_supplier_account
        bk_username
        """
        return await self.bk_sops_api.call_action(f'start_task/', 'POST', json=params)


class SopsV3:
    """
    sops api shortcut
    """

    def __init__(self, bk_sops_api: BKApi):
        self.bk_sops_api = bk_sops_api

    async def get_template_info(self, bk_biz_id, template_id, **params) -> Dict:
        """
        -params:
        template_id
        bk_biz_id
        """
        return await self.bk_sops_api.call_action(f'get_template_info/{template_id}/{bk_biz_id}/',
                                                  'GET', params=params)

    async def get_template_schemes(self, bk_biz_id, template_id, **params) -> Dict:
        """
        -params:
        template_id
        bk_biz_id
        """
        return await self.bk_sops_api.call_action(f'get_template_schemes/{bk_biz_id}/{template_id}/',
                                                  'GET', params=params)

    async def get_template_list(self, bk_biz_id, **params) -> Dict:
        """
        -params:
        bk_biz_id
        """
        return await self.bk_sops_api.call_action(f'get_template_list/{bk_biz_id}/', 'GET', params=params)

    async def create_task(self, bk_biz_id, template_id, **params) -> Dict:
        """
        -params:
        template_id
        bk_biz_id
        -body
        constants
        exclude_task_nodes_id
        name
        bk_supplier_account
        bk_username
        """
        return await self.bk_sops_api.call_action(f'create_task/{template_id}/{bk_biz_id}/',
                                                  'POST', json=params)

    async def start_task(self, bk_biz_id, task_id, **params) -> Dict:
        """
        -params:
        task_id
        bk_biz_id
        -body
        bk_supplier_account
        bk_username
        """
        return await self.bk_sops_api.call_action(f'start_task/{task_id}/{bk_biz_id}/',
                                                  'POST', json=params)

    async def get_mini_app_list(self, bk_biz_id, **params):
        return await self.bk_sops_api.call_action(f'get_mini_app_list/{bk_biz_id}/',
                                                  'GET', params=params)


class DevOps:
    """
    devops api shortcut
    """

    def __init__(self, bk_devops_api: BKApi):
        self.bk_devops_api = bk_devops_api

    async def v3_app_project_list(self, bk_username) -> List:
        return await self.bk_devops_api.call_action(f'projects/',
                                                    'GET', headers={'X-DEVOPS-UID': bk_username})

    async def v3_app_pipeline_list(self, project_id, bk_username) -> Dict:
        return await self.bk_devops_api.call_action(f'projects/{project_id}/pipelines/',
                                                    'GET', headers={'X-DEVOPS-UID': bk_username})

    async def v3_app_build_start_info(self, project_id, pipeline_id, bk_username) -> Dict:
        return await self.bk_devops_api.call_action(
            f'projects/{project_id}/pipelines/{pipeline_id}/builds/manualStartupInfo', 'GET',
            headers={'X-DEVOPS-UID': bk_username})

    async def v3_app_build_start(self, project_id, pipeline_id, bk_username, **params) -> Dict:
        return await self.bk_devops_api.call_action(f'projects/{project_id}/pipelines/{pipeline_id}/builds/start',
                                                    'POST', headers={'X-DEVOPS-UID': bk_username}, json=params)


class BKBase:
    """
    BKBase api shortcut
    """

    def __init__(self, api_root: str, app_id: str, app_secret: str, method='token', token=None):
        self._auth = {
            'bk_app_code': app_id,
            'bk_app_secret': app_secret,
            'bkdata_authentication_method': method,
            'bkdata_data_token': token
        }
        self.bk_data_api = BKApi(api_root, app_id, app_secret)

    async def data_query(self, **params) -> List:
        params.update(self._auth)
        return await self.bk_data_api.call_action(f'prod/v3/dataquery/query/', 'POST', json=params)


class ITSM:
    """
    ITSM ticket api shortcut
    """

    def __init__(self, bk_itsm_api: BKApi):
        self.bk_itsm_api = bk_itsm_api

    async def operate_node(self, **params) -> Dict:
        """
        {
            "sn": "NO2019110816441094",
            "operator": "zhangsan",
            "action_type": "TRANSITION",
            "state_id": 4,
            "fields": [{
                "key": "SHENPIJIEGUO",
                "value": "TONGYI"
            }]
        }
        """
        return await self.bk_itsm_api.call_action('prod/v2/itsm/operate_node/', 'POST', json=params)

    async def create_ticket(self, **params):
        """
        service_id
        creator:
        fields:
         -urgency: 1/2/3
         -bk_biz_id: 820
         -remark
         -event_type: pro/pre/test
         -start_date
         -end_date
         -members: neolei
         -impact: 1/2/3
         -priority: 1/2/3
        """

        return await self.bk_itsm_api.call_action('create_ticket/', 'POST', json=params)

    async def get_tickets(self, page, page_size, **params):
        """
        filter:
        -sns: ["NO2019091610001755"]
        -create_at__lte: "2019-09-16 10:00:00"
        -service_id: [24, 57]
        """

        return await self.bk_itsm_api.call_action('get_tickets/', 'POST', json=params,
                                                  params={'ordering': 'create_at',
                                                          'page': page, 'page_size': page_size})

    async def get_services(self, **params):
        return await self.bk_itsm_api.call_action('get_services/', 'GET', params=params)


class JobV2:
    def __init__(self, bk_job_v2_api: BKApi):
        self.bk_job_v2_api = bk_job_v2_api

    async def execute_job(self, **params) -> Any:
        """
        -params:
        bk_biz_id
        bk_job_id
        global_var_list
        steps
        bk_username
        """
        return await self.bk_job_v2_api.call_action('execute_job/', 'POST', json=params)
