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
from common.utils.os import get_env_or_raise
from src.manager.module_intent.models import ExecutionLog

ONE_WEEK_SECONDS = 60 * 60 * 24 * 7


# 定时任务
UPDATE_TASK_TIME = get_env_or_raise("UPDATE_TASK_TIME", 30)  # 更新任务时间间隔
UPDATE_TASK_MAX_WORKERS = get_env_or_raise("UPDATE_TASK_TIME", 10)  # 最大线程
UPDATE_TASK_MAX_TIME = get_env_or_raise("UPDATE_TASK_TIME", 24 * 60 * 60)  # 任务保留时间
UPDATE_TASK_LOG = "task_log"
UPDATE_TASK_PREFIX = "task_log_"  # 任务redis key前缀
TASK_NOTICE_PREFIX = "task_notice"  # 机器人日志通知前缀

# 任务状态中文
TASK_EXECUTE_STATUS_DICT = {
    ExecutionLog.TaskExecStatus.INIT.value: "初始状态",
    ExecutionLog.TaskExecStatus.RUNNING.value: "执行中",
    ExecutionLog.TaskExecStatus.SUCCESS.value: "执行成功",
    ExecutionLog.TaskExecStatus.FAIL.value: "执行失败",
    ExecutionLog.TaskExecStatus.SUSPENDED.value: "暂停",
    ExecutionLog.TaskExecStatus.REMOVE.value: "执行终止",
}

# 任务执行颜色
TASK_EXEC_STATUS_COLOR_DICT = {
    ExecutionLog.TaskExecStatus.INIT.value: "#B0BEC5",
    ExecutionLog.TaskExecStatus.RUNNING.value: "#4FC3F7",
    ExecutionLog.TaskExecStatus.SUCCESS.value: "#00FF00",
    ExecutionLog.TaskExecStatus.FAIL.value: "#E53935",
    ExecutionLog.TaskExecStatus.SUSPENDED.value: "#FFEE58",
    ExecutionLog.TaskExecStatus.REMOVE.value: "#E53935",
}


# 环境变量获取
JOB_HOST = get_env_or_raise("BKAPP_JOB_HOST")
DEVOPS_HOST = get_env_or_raise("BKAPP_DEVOPS_HOST")
