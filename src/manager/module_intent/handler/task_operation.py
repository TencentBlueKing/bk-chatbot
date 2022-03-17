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
from common.constants import PlatformType
from common.design.strategy import Strategy
from module_intent.handler.task_devops import DevOps
from module_intent.handler.task_job import Job
from module_intent.handler.task_sops import Sops
from module_intent.models import ExecutionLog


class Operation(Strategy):

    _map = dict()

    @classmethod
    def do(cls, action: int, id: int, data: dict):
        """
        执行操作
        @param action:
        @param id:
        @param data:
        @return:
        """
        # 通过id查询对应的数据
        task_log = ExecutionLog.objects.get(pk=id)
        return cls._map.value[task_log.platform](action, task_log, data)


@Operation.register(PlatformType.JOB.value)
def do_job(action: int, obj: ExecutionLog, data):
    """
    执行job
    """
    ret = Job.do(action, obj, data)
    return ret


@Operation.register(PlatformType.SOPS.value)
def do_sops(action: int, obj: ExecutionLog, data):
    """
    执行标准运维
    """
    ret = Sops.do(action, obj, data)
    return ret


@Operation.register(PlatformType.DEV_OPS.value)
def do_devops(action: int, obj: ExecutionLog, data):
    """
    执行蓝盾
    """
    ret = DevOps.do(action, obj, data)
    return ret
