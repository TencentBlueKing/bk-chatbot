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

from component.bk.api import (
    BKApi, CC, ITSM, JOB, SopsV3, DevOps, Backend
)
from .base import BkService as BaseBkService


class BKService(BaseBkService):
    __slots__ = ['cc', 'job', 'sops', 'devops', 'itsm', 'backend']

    def __init__(self):
        super().__init__('v7', 'bk', 'V7', '7.0')
        self.cc = CC(BKApi(self.BK_CC_ROOT, *self.BK_TOKEN))
        self.itsm = ITSM(BKApi(self.BK_ITSM_ROOT, *self.BK_TOKEN))
        self.backend = Backend(self.BACKEND_ROOT, *self.BK_TOKEN)
        self.job = JOB(BKApi(self.BK_JOB_ROOT, *self.BK_TOKEN))
        self.sops = SopsV3(BKApi(self.BK_SOPS_ROOT, *self.BK_TOKEN))
        self.devops = DevOps(BKApi(self.BK_DEVOPS_ROOT, *self.BK_TOKEN))
        self.backend = Backend(self.BACKEND_ROOT, *self.BK_TOKEN)
