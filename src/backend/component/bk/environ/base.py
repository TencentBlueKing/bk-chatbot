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

import os
import re
import json
import itertools
from typing import Dict, List, Optional, Callable


class BkService:
    def __init__(self, name: str, operator: str, prefix: str, version: str):
        self.name = name
        self.operator = operator
        self.prefix = prefix
        self.version = version

        self.BK_APP_ID = os.getenv(f'{prefix}_BK_APP_ID', '')
        self.BK_APP_SECRET = os.getenv(f'{prefix}_BK_APP_SECRET', '')
        self.BK_BASE_TOKEN = os.getenv(f'{prefix}_BK_BASE_TOKEN', '')

        self.BK_PAAS_DOMAIN = os.getenv(f'{prefix}_BK_PAAS_DOMAIN', '')
        self.BK_CHAT_DOMAIN = os.getenv(f'{prefix}_BK_CHAT_DOMAIN', '')
        self.BK_CC_DOMAIN = os.getenv(f'{prefix}_BK_CC_DOMAIN', '')
        self.BK_JOB_DOMAIN = os.getenv(f'{prefix}_BK_JOB_DOMAIN', '')
        self.BK_SOPS_DOMAIN = os.getenv(f'{prefix}_BK_SOPS_DOMAIN', '')
        self.BK_DEVOPS_DOMAIN = os.getenv(f'{prefix}_BK_DEVOPS_DOMAIN', '')
        self.BK_BASE_DOMAIN = os.getenv(f'{prefix}_BK_BASE_DOMAIN', '')
        self.BK_ITSM_DOMAIN = os.getenv(f'{prefix}_BK_ITSM_DOMAIN', '')

        self.BK_CC_ROOT = os.getenv(f'{prefix}_BK_CC_ROOT', '')
        self.BK_JOB_ROOT = os.getenv(f'{prefix}_BK_JOB_ROOT', '')
        self.BK_SOPS_ROOT = os.getenv(f'{prefix}_BK_SOPS_ROOT', '')
        self.BK_DEVOPS_ROOT = os.getenv(f'{prefix}_BK_DEVOPS_ROOT', '')
        self.BK_BASE_ROOT = os.getenv(f'{prefix}_BK_DATA_ROOT', '')
        self.BK_ITSM_ROOT = os.getenv(f'{prefix}_BK_ITSM_ROOT', '')
        self.BACKEND_ROOT = os.getenv(f'{prefix}_BACKEND_ROOT', '')

        self.BK_TOKEN = self.BK_APP_ID, self.BK_APP_SECRET


class BKTask:
    def __init__(self, bk_service: BkService):
        self._bk_service = bk_service

    async def _bk_job(self,
                      task: Dict,
                      slots: List,
                      biz_id: Optional[str],
                      executor: str,
                      validate_ip: Callable,
                      ip_pattern: str):
        global_var_list = [{
            'name': slot.get('name'), 'value': slot.get('value')
        } for slot in slots if slot.get('type') == 1]

        global_var_list.extend([{'id': slot.get('id'), 'server': {
            'ip_list': [{'bk_cloud_id': 0, 'ip': ip} for ip in re.split('[\n\s,;]\s*', slot['value'])]
        }} for slot in slots if slot.get('type') == 3 and validate_ip(ip_pattern, slot.get('value'))])

        response = await self._bk_service.job.execute_job_plan(
            bk_biz_id=biz_id,
            job_plan_id=int(task.get('task_id')),
            global_var_list=global_var_list,
            bk_username=executor
        )
        return {
            'url': f'{self._bk_service.BK_JOB_DOMAIN}biz/{task.get("biz_id")}/execute'
                   f'/task/{response.get("job_instance_id")}',
            'platform': 1,
            'task_id': response.get("job_instance_id")
        }

    async def _bk_sops(self,
                       task: Dict,
                       slots: List,
                       biz_id: Optional[str],
                       executor: str):
        source = task.get('source', {})
        activities = [
            k for k, v in source.get('pipeline_tree', {}).get('activities').items()
            if v['optional']
        ]
        select_group = list(
            itertools.chain(*[json.loads(node['data']) for node in task.get('activities', []) if node])
        )
        exclude_task_nodes_id = list(
            set(activities).difference(set(select_group))
        ) if select_group else []
        constants = {slot['id']: slot['value'] for slot in slots}

        response = await self._bk_service.sops.create_task(bk_biz_id=biz_id,
                                                          template_id=task.get('task_id'),
                                                          name=source.get('name'),
                                                          bk_username=executor,
                                                          exclude_task_nodes_id=exclude_task_nodes_id,
                                                          constants=constants)

        await self._bk_service.sops.start_task(bk_biz_id=biz_id, task_id=str(response.get('task_id')),
                                              bk_username=executor)
        return {
            'url': response.get('task_url'),
            'platform': 2,
            'task_id': response.get("task_id")
        }

    async def _bk_devops(self,
                         task: Dict,
                         slots: List,
                         biz_id: Optional[str],
                         executor: str):
        project_id = task.get('project_id')
        pipeline_id = task.get('task_id')
        params = {slot['name']: slot['value'] for slot in slots}
        response = await self._bk_service.devops.v3_app_build_start(project_id, pipeline_id, executor, **params)
        detail_id = response.get("id")
        return {
            'url': f'{self._bk_service.BK_DEVOPS_DOMAIN}console/pipeline/{project_id}/{pipeline_id}/detail/{detail_id}',
            'platform': 3,
            'task_id': detail_id,
            'project_id': project_id,
            'pipeline_id': pipeline_id
        }
