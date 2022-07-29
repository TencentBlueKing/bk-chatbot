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


import traceback
from typing import Callable

from blueapps.utils.logger import logger_celery as logger

from common.design.strategy import Strategy
from common.models.base import to_format_date
from common.redis import RedisClient
from src.manager.handler.api.message import Message
from src.manager.handler.bk.bk_devops import BkDevOps
from src.manager.handler.bk.bk_job import BkJob
from src.manager.handler.bk.bk_sops import BkSops
from src.manager.module_intent.constants import (
    TASK_EXEC_STATUS_COLOR_DICT,
    TASK_EXECUTE_STATUS_DICT,
    TASK_NOTICE_PREFIX,
    UPDATE_TASK_MAX_TIME,
    UPDATE_TASK_PREFIX,
)
from src.manager.module_intent.models import ExecutionLog


def update_task_status(id: int) -> None:
    """
    更新任务状态
    :param id:
    :return:
    """
    logger.info(f"更新任务ID:{id}")
    execution_log_obj: ExecutionLog = ExecutionLog.query_log(id)
    TaskStatus.do(execution_log_obj)


class PlatformTask:
    def __init__(self, obj: ExecutionLog):
        self.obj = obj

    def get_task_cache(self, key):
        """
        获取缓存数据
        @param key:
        @return:
        """
        with RedisClient() as r:
            return r.keys(f"{UPDATE_TASK_PREFIX}{key}")

    def del_task_cache(self, key):
        """
        删除任务缓存
        @return:
        """
        with RedisClient() as r:
            r.expire(f"{UPDATE_TASK_PREFIX}{key}", 0)

    def set_notice_cache(self, key, value):
        """
        设置通知的缓存
        @param key:
        @param value:
        @return:
        """
        new_key = f"{TASK_NOTICE_PREFIX}_{key}"
        redis_client = RedisClient()
        return redis_client.set_nx(new_key, value, UPDATE_TASK_MAX_TIME + 600)

    def save_task(self, func: Callable, **kwargs):
        """
        保存任务日志信息
        @param func:
        @param kwargs:
        @return:
        """
        try:
            task_info = func(**kwargs)
            logger.info(f"获取任务详情:{task_info}")
            status = task_info.get("status")
            self.obj.status = status
            self.obj.save()
            return task_info
        except Exception as e:  # pylint: disable=broad-except
            # 异常删除缓存信息
            traceback.print_exc()
            logger.error(f"更新日志状态异常:{e}")
            self.del_task_cache(self.obj.id)
            raise e

    def callback(self, task_uri: str, param_list: list):
        """消息通知
        :param obj:
        :param uri:
        :return:
        """
        try:
            status = TASK_EXECUTE_STATUS_DICT.get(self.obj.status)
            color = TASK_EXEC_STATUS_COLOR_DICT.get(self.obj.status)
            receiver = self.obj.rtx if self.obj.rtx else self.obj.sender
            params = {
                "log_id": self.obj.id,
                "biz_id": self.obj.biz_id,
                "bot_name": self.obj.bot_name,
                "user": self.obj.sender,
                "receiver": receiver,  # rtx(个人/群);游梯对象(openid)
                "intent_name": self.obj.intent_name,
                "intent_id": self.obj.intent_id,
                "status": status,
                "color": color,
                "task_uri": task_uri,
                "time": to_format_date(self.obj.updated_at),
                "param_list": param_list,
            }

            # 消息通知失败也不会再进行查询
            try:

                # 不通知的情况
                # 1、没有缓存
                # 2、有缓存,状态为成功并且执行通知为false
                if self.get_task_cache(self.obj.id) and (
                    self.obj.status != ExecutionLog.TaskExecStatus.SUCCESS.value or self.obj.notice_exec_success
                ):
                    Message.notice(**params)

            except Exception:  # pylint: disable=broad-except
                traceback.print_exc()
                logger.error(f"发送通知错误:{traceback.format_exc()}")
            # 如果出现状态为成功/移除 则删除
            if self.obj.status in [
                ExecutionLog.TaskExecStatus.SUCCESS.value,
                ExecutionLog.TaskExecStatus.REMOVE.value,
            ]:
                self.del_task_cache(self.obj.id)
        except ValueError:
            traceback.print_exc()
            logger.error(f"发送通知错误:{traceback.format_exc()}")
        except Exception:  # pylint: disable=broad-except
            traceback.print_exc()
            logger.error(f"发送通知错误:{traceback.format_exc()}")


class TaskStatus(Strategy):
    """
    更新执行日志状态
    """

    _map = dict()

    @classmethod
    def do(cls, obj: ExecutionLog):
        """
        更新状态
        """
        platform = int(obj.platform)
        task_class = PlatformTask(obj=obj)
        ret_dict = cls._map.value[platform](task_class)
        if not ret_dict:
            return
        task_class.callback(**ret_dict)


@TaskStatus.register(ExecutionLog.PlatformType.JOB.value)
def job(task_class: PlatformTask):
    """
    作业平台
    :param obj:
    :return:
    """

    bk_job = BkJob(
        biz_id=task_class.obj.biz_id,
        username=task_class.obj.intent_create_user,
        task_id=task_class.obj.task_id,
    )

    job_ret = task_class.save_task(
        func=bk_job.get_job_instance_status,
    )
    status = job_ret.get("status")
    if status not in [
        ExecutionLog.TaskExecStatus.SUCCESS.value,
        ExecutionLog.TaskExecStatus.FAIL.value,
        ExecutionLog.TaskExecStatus.REMOVE.value,
    ]:
        return {}
    param_uniq_list = bk_job.get_uniq_var_value()  # 去重后参数
    if status == ExecutionLog.TaskExecStatus.SUCCESS.value:  # 成功通知
        return {
            "task_uri": bk_job.url,
            "param_list": param_uniq_list,
        }

    job_instance = job_ret["data"].get("job_instance", {})
    end_time = job_instance.get("end_time")
    key = f"{task_class.obj.id}_{task_class.obj.task_id}_{status}_{end_time}"  # 通过步骤ID来进行告警
    if task_class.set_notice_cache(key, ""):
        return {
            "task_uri": bk_job.url,
            "param_list": param_uniq_list,
        }


@TaskStatus.register(ExecutionLog.PlatformType.SOPS.value)
def sops(task_class: PlatformTask):
    """
    标准运维
    :param obj:
    :return:
    """

    bk_sops = BkSops(
        username=task_class.obj.intent_create_user,
        biz_id=task_class.obj.biz_id,
        task_id=task_class.obj.task_id,
    )
    sops_ret = task_class.save_task(func=bk_sops.get_task_status)
    status = sops_ret.get("status")
    if status not in [
        ExecutionLog.TaskExecStatus.SUCCESS.value,
        ExecutionLog.TaskExecStatus.FAIL.value,
        ExecutionLog.TaskExecStatus.REMOVE.value,
    ]:
        return {}

    # 查询标准运维的详情
    if status == ExecutionLog.TaskExecStatus.SUCCESS.value:  # 成功通知
        return {
            "task_uri": bk_sops.task_uri,
            "param_list": bk_sops.params,
        }

    state_refresh_at = sops_ret.get("data", {}).get("state_refresh_at")
    key = f"{task_class.obj.id}_{task_class.obj.task_id}_{status}_{state_refresh_at}"  # 通过步骤ID来进行告警
    if task_class.set_notice_cache(key, ""):
        return {
            "task_uri": bk_sops.task_uri,
            "param_list": bk_sops.params,
        }


@TaskStatus.register(ExecutionLog.PlatformType.DEV_OPS.value)
def dev_ops(task_class: PlatformTask):
    """
    @param task_class:
    @return:
    """

    bk_devops = BkDevOps(
        username=task_class.obj.intent_create_user,
        project_id=task_class.obj.project_id,
        pipeline_id=task_class.obj.feature_id,
        build_id=task_class.obj.task_id,
    )
    dev_ops_ret = task_class.save_task(
        func=bk_devops.get_build_status,
    )

    # 1.判断状态，2.通过状态判断是否通知 3.查询参数
    status = dev_ops_ret.get("status", "")
    if status not in [
        ExecutionLog.TaskExecStatus.SUCCESS.value,
        ExecutionLog.TaskExecStatus.FAIL.value,
        ExecutionLog.TaskExecStatus.REMOVE.value,
    ]:
        return {}

    data_dict = dev_ops_ret.get("data", "")
    params = data_dict.get("buildParameters", [])  # 流水线参数
    param_list = list(
        map(
            lambda x: {
                "name": x.get("key"),
                "value": x.get("value"),
            },
            params,
        )
    )

    if status == ExecutionLog.TaskExecStatus.SUCCESS.value:  # 成功通知
        return {
            "task_uri": bk_devops.pipeline_url,
            "param_list": param_list,
        }

    stage_status_list = data_dict.get("stageStatus", [])
    stage_error_status = list(
        filter(
            lambda x: x.get("status") in ["CANCELED", "FAILED"],
            stage_status_list,
        )
    )
    if len(stage_error_status) != 1:
        return
    # 异常节点状态
    fail_stage_status = stage_error_status[-1]
    last_stage_id = fail_stage_status.get("stageId", None)  # 异常的stage的ID
    last_start_epoch = fail_stage_status.get("startEpoch", None)  # 异常stage开始时间
    key = f"{task_class.obj.id}_{last_stage_id}_{status}_{last_start_epoch}"
    if task_class.set_notice_cache(key, ""):
        return {
            "task_uri": bk_devops.pipeline_url,
            "param_list": param_list,
        }
