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


import asyncio
from typing import Callable

from common.design.strategy import Strategy
from src.manager.handler.api.devops import DevOps
from src.manager.handler.api.bk_job import JOB
from src.manager.handler.api.bk_sops import SOPS
from src.manager.module_intent.models import ExecutionLog


async def callback(func: Callable, bk_username: str, bk_biz_id: int, task_id: str) -> dict:
    """
    获取sops错误的节点的日志
    """
    ret = func(
        bk_username=bk_username,
        bk_biz_id=bk_biz_id,
        task_id=task_id,
    )
    return ret


class Pipeline(Strategy):
    """
    流程
    """

    _map = dict()

    @classmethod
    def make(cls, id):
        """
        生成执行树
        """
        execution_log_obj: ExecutionLog = ExecutionLog.query_log(**{"id": id})
        platform = int(execution_log_obj.platform)
        return cls._map.value[platform](execution_log_obj)


@Pipeline.register(ExecutionLog.PlatformType.JOB.value)
def make_job_pipeline(obj: ExecutionLog):
    """
    生成作业平台 pipeline
    """
    ret = JOB.get_job_instance_status(
        bk_username=obj.intent_create_user,
        bk_biz_id=obj.biz_id,
        job_instance_id=obj.task_id,
    )
    data = ret.get("data")
    data.setdefault("platform", obj.platform)
    return data


@Pipeline.register(ExecutionLog.PlatformType.SOPS.value)
def make_sops_pipeline(obj: ExecutionLog):
    """
    生成标准运维 pipeline
    """

    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()

    # 查询详情
    task_detail = loop.create_task(
        callback(
            SOPS.get_task_detail,
            obj.intent_create_user,
            obj.biz_id,
            obj.task_id,
        )
    )
    # 查询状态
    task_status = loop.create_task(
        callback(
            SOPS.get_task_status,
            obj.intent_create_user,
            obj.biz_id,
            obj.task_id,
        )
    )

    tasks = [task_detail, task_status]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    # 结果获取
    data: dict = task_detail.result()
    data.setdefault("children", task_status.result().get("data", {}).get("children"))
    data.setdefault("platform", obj.platform)
    return data


@Pipeline.register(ExecutionLog.PlatformType.DEV_OPS.value)
def make_devops_pipeline(obj: ExecutionLog):
    """
    生成蓝盾 pipeline
    """

    ret = DevOps.app_build_detail(
        bk_username=obj.intent_create_user,
        project_id=obj.project_id,
        pipeline_id=obj.feature_id,
        build_id=obj.task_id,
    )
    data = ret.get("data")
    data.setdefault("platform", obj.platform)
    return data
