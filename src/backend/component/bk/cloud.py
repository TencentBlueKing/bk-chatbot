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

from importlib import import_module
from typing import Dict, List, Optional, Callable

from .environ.base import BKTask as BaseBKTask


class BKCloud(BaseBKTask):
    def __init__(self, env: str = 'v7'):
        module = import_module(f'component.bk.environ.{env}')
        self.bk_service = module.BKService()
        super().__init__(self.bk_service)

    async def bk_sops(self,
                      task: Dict,
                      slots: List,
                      biz_id: Optional[str],
                      executor: str):
        try:
            sops_func = getattr(self.bk_service, '_bk_sops')
        except AttributeError:
            sops_func = self._bk_sops
        return await sops_func(task, slots, biz_id, executor)

    async def bk_job(self,
                     task: Dict,
                     slots: List,
                     biz_id: Optional[str],
                     executor: str,
                     validate_ip: Callable,
                     ip_pattern: str):
        try:
            job_func = getattr(self.bk_service, '_bk_job')
        except AttributeError:
            job_func = self._bk_job
        return await job_func(task, slots, biz_id, executor, validate_ip, ip_pattern)

    async def bk_devops(self,
                        task: Dict,
                        slots: List,
                        biz_id: Optional[str],
                        executor: str):
        try:
            devops_func = getattr(self.bk_service, '_bk_devops')
        except AttributeError:
            devops_func = self._bk_devops
        return await devops_func(task, slots, biz_id, executor)

    async def set_timer(self, biz_id, intent_name, timestamp, user_id, exec_data):
        self.bk_service.backend.set_timer(biz_id=biz_id, timer_name=intent_name,
                                          execute_time=timestamp, timer_status=1, timer_user=user_id,
                                          exec_data=exec_data, expression='')

    async def describe_entity(self, entity: str, **params):
        return await self.bk_service.backend.describe(entity, **params)
