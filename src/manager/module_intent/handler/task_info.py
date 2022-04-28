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

from common.design.strategy import Strategy
from src.manager.handler.api.bk_job import JOB
from src.manager.handler.api.bk_sops import SOPS
from src.manager.handler.api.devops import DevOps
from src.manager.module_intent.models import ExecutionLog


async def get_sops_error(bk_username: str, bk_biz_id: int, task_id: str, node_id: str) -> dict:
    """
    获取sops错误的节点的日志
    """
    ret = SOPS.get_task_node_detail(
        bk_username=bk_username,
        bk_biz_id=bk_biz_id,
        task_id=task_id,
        node_id=node_id,
    )
    return ret.get("data")


class TaskDetail(Strategy):

    _map = dict()

    @classmethod
    def get(cls, id: int):
        """
        更新状态
        """

        execution_log_obj: ExecutionLog = ExecutionLog.query_log(id)
        platform = int(execution_log_obj.platform)
        return cls._map.value[platform](execution_log_obj)


@TaskDetail.register(ExecutionLog.PlatformType.JOB.value)
def job(obj: ExecutionLog):
    """
    作业平台
    :param obj:
    :return:
    """
    ret = JOB.get_job_instance_status(
        bk_username=obj.intent_create_user,
        bk_biz_id=obj.biz_id,
        job_instance_id=obj.task_id,
        return_ip_result=True,
    )

    step_instance_list = ret.get("data", {}).get("step_instance_list", [])
    # 执行失败的步骤
    error_step = list(filter(lambda x: x.get("status") == 4, step_instance_list))
    if len(error_step) == 0:
        return
    # 执行失败的IP
    step_error_ip_list = list(filter(lambda x: x.get("status") != 9, error_step[0].get("step_ip_result_list")))
    if len(step_error_ip_list) == 0:
        return
    error_step_instance_id = error_step[0].get("step_instance_id")  # 错误步骤id
    error_ip = step_error_ip_list[0].get("ip")  # 错误ip
    bk_cloud_id = step_error_ip_list[0].get("bk_cloud_id")

    # 错误IP日志打印信息
    instance_ip_ret = JOB.get_job_instance_ip_log(
        bk_username=obj.intent_create_user,
        bk_biz_id=obj.biz_id,
        job_instance_id=int(obj.task_id),
        step_instance_id=error_step_instance_id,
        bk_cloud_id=bk_cloud_id,
        ip=error_ip,
    )

    ip_error_data = instance_ip_ret.get("data")
    ip_error_infos = [
        {
            "bk_biz_id": str(obj.biz_id),
            "task_id": obj.task_id,
            "node_id": str(error_step_instance_id),
            "node_name": error_step[0].get("name"),
            "ip": ip_error_data.get("ip"),
            "error_msg": ip_error_data.get("log_content"),
        }
    ]

    return ip_error_infos


@TaskDetail.register(ExecutionLog.PlatformType.SOPS.value)
def sops(obj: ExecutionLog):
    """
    标准运维
    :param obj:
    :return:
    """

    # 查询状态
    ret = SOPS.get_task_status(
        bk_username=obj.intent_create_user,
        bk_biz_id=obj.biz_id,
        task_id=obj.task_id,
    )

    # 通过状态查询错误节点日志
    children = ret.get("data", {}).get("children", {})
    # 函数拼接
    tasks = list(
        map(
            lambda x: get_sops_error(
                **{
                    "bk_username": obj.intent_create_user,
                    "bk_biz_id": obj.biz_id,
                    "task_id": obj.task_id,
                    "node_id": x.get("id"),
                }
            ),
            filter(lambda value: value.get("state") == "FAILED", children.values()),
        )
    )

    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    data, _ = loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    # 错误信息处理
    error_infos = list(
        map(
            lambda x: {
                "bk_biz_id": str(obj.biz_id),
                "task_id": obj.task_id,
                "node_id": str(x.result().get("id")),
                "node_name": x.result().get("name"),
                "error_msg": x.result().get("ex_data"),
            },
            data,
        )
    )

    return error_infos


@TaskDetail.register(ExecutionLog.PlatformType.DEV_OPS.value)
def dev_ops(obj: ExecutionLog):
    """
    蓝盾
    :param obj:
    :return:
    """

    ret = DevOps.app_build_status(
        bk_username=obj.intent_create_user,
        project_id=obj.project_id,
        pipeline_id=obj.feature_id,
        build_id=obj.task_id,
    )
    error_info_list = ret.get("data", {}).get("errorInfoList", [])
    error_infos = list(
        map(
            lambda error_info: {
                "bk_biz_id": obj.biz_id,
                "project_id": obj.project_id,
                "pipeline_id": obj.feature_id,
                "task_id": obj.task_id,
                "node_id": error_info.get("taskId"),
                "node_name": error_info.get("taskName"),
                "error_msg": error_info.get("errorMsg"),
            },
            error_info_list,
        )
    )
    return error_infos
