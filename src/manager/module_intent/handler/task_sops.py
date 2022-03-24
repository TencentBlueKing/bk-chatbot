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
from src.manager.handler.bk.bk_sops import BkSops
from src.manager.module_intent.handler import TaskType
from src.manager.module_intent.models import ExecutionLog


class Sops(Strategy):

    _map = dict()

    @classmethod
    def do(cls, action: int, obj: ExecutionLog, data: dict):
        bk_sops = BkSops(
            username=obj.intent_create_user,
            biz_id=obj.biz_id,
            task_id=obj.task_id,
        )
        return cls._map.value[action](bk_sops, **data)


@Sops.register(TaskType.STOP.value)
def stop(bk_sops: BkSops, **kwargs):
    """
    流程停止
    @param bk_sops:
    @param kwargs:
    @return:
    """
    ret = bk_sops.revoke_task()
    return ret


@Sops.register(TaskType.PAUSE.value)
def pause(bk_sops: BkSops, **kwargs):
    """
    流程暂停
    @param bk_sops:
    @param kwargs:
    @return:
    """
    ret = bk_sops.pause_task()
    return ret


@Sops.register(TaskType.RETRY.value)
def retry(bk_sops: BkSops, **kwargs):
    """
    重试节点
    @param bk_sops:
    @param kwargs:
    @return:
    """
    node_id = kwargs.get("node_id")
    ret = bk_sops.retry_node(node_id)
    return ret


@Sops.register(TaskType.SKIP.value)
def skip(bk_sops: BkSops, **kwargs):
    """
    跳过节点
    @param bk_sops:
    @param kwargs:
    @return:
    """
    node_id = kwargs.get("node_id")
    ret = bk_sops.skip_node(node_id)
    return ret
