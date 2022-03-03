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


from common.design.strategy import Strategy
from src.manager.handler.bk.bk_job import BkJob
from src.manager.module_intent.handler import TaskType
from src.manager.module_intent.models import ExecutionLog


class Job(Strategy):

    _map = dict()

    @classmethod
    def do(cls, action: int, obj: ExecutionLog, data: dict):

        # 通过id查询对应的数据
        bk_job = BkJob(obj.biz_id, obj.intent_create_user, obj.task_id)
        return cls._map.value[action](bk_job, **data)


@Job.register(TaskType.STOP.value)
def stop(bk_job: BkJob, **kwargs):
    """
    停止
    @return:
    """
    ret = bk_job.terminate()
    return ret


@Job.register(TaskType.PAUSE.value)
def pause(bk_job: BkJob, **kwargs):
    """
    暂停暂时没有对应的操作
    @param obj:
    @param kwargs:
    @return:
    """
    raise ValueError("JOB作业没有暂停操作")


@Job.register(TaskType.RETRY.value)
def retry(bk_job: BkJob, **kwargs):
    """
    重试
    @return:
    """

    ret = bk_job.retry_fail()
    return ret


@Job.register(TaskType.SKIP.value)
def skip(bk_job: BkJob, **kwargs):
    """
    跳过
    @return:
    """
    ret = bk_job.ignore_error()
    return ret
