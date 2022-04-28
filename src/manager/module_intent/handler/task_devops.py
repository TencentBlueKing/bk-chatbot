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
from src.manager.handler.bk.bk_devops import BkDevOps
from src.manager.module_intent.handler import TaskType
from src.manager.module_intent.models import ExecutionLog


class DevOps(Strategy):
    _map = dict()

    @classmethod
    def do(cls, action: int, obj: ExecutionLog, data: dict):
        # 通过id查询对应的数据
        bk_dev_ops = BkDevOps(
            username=obj.intent_create_user,
            project_id=obj.project_id,
            pipeline_id=obj.feature_id,
            build_id=obj.task_id,
        )
        return cls._map.value[action](bk_dev_ops, **data)


@DevOps.register(TaskType.STOP.value)
def stop(bk_dev_ops, **kwargs):
    """
    停止流程
    @param bk_dev_ops:
    @param kwargs:
    @return:
    """
    ret = bk_dev_ops.stop_pipeline()
    return ret


@DevOps.register(TaskType.PAUSE.value)
def pause(bk_dev_ops: BkDevOps, **kwargs):
    """
    暂停
    @param bk_dev_ops:
    @param kwargs:
    @return:
    """
    # ret = bk_dev_ops.operate_pipeline()
    # return ret
    pass


@DevOps.register(TaskType.RETRY.value)
def retry(bk_dev_ops: BkDevOps, **kwargs):
    """
    重试
    @param bk_dev_ops:
    @param kwargs:
    @return:
    """
    task_id = kwargs.get("task_id")
    ret = bk_dev_ops.retry(task_id)
    return ret


@DevOps.register(TaskType.SKIP.value)
def skip(bk_dev_ops: BkDevOps, **kwargs):
    """
    跳过
    @param bk_dev_ops:
    @param kwargs:
    @return:
    """
    task_id = kwargs.get("task_id")
    ret = bk_dev_ops.skip(task_id)
    return ret
