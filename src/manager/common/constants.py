# -*- coding: utf-8 -*-

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
import os
from enum import Enum

from django.utils.translation import ugettext_lazy as _

# 机器人类型
CHAT_BOT_TYPE_WEWORK = "xwork"
CHAT_BOT_TYPE_QQ = "qq"
CHAT_BOT_TYPE_WX = "wechat"
CHAT_BOT_TYPE_SLACK = "slack"
CHAT_BOT_TYPE_DEFAULT = "default"
STAG_PLUGIN_URI_ENV = "STAG_PLUGIN_URI"
PROD_PLUGIN_URI_ENV = "PROD_PLUGIN_URI"


CHAT_BOT_TYPES = (
    (CHAT_BOT_TYPE_WEWORK, _("企业微信")),
    (CHAT_BOT_TYPE_QQ, _("QQ")),
    (CHAT_BOT_TYPE_WX, _("微信")),
    (CHAT_BOT_TYPE_SLACK, _("SLACK")),
    (CHAT_BOT_TYPE_DEFAULT, _("OPSBOT")),
)

# 任务平台
TAK_PLATFORM_JOB = "JOB"
TAK_PLATFORM_SOPS = "SOPS"
TAK_PLATFORM_DEVOPS = "DEVOPS"
TAK_PLATFORM_DEFINE = "DEFINE"

TASK_PLATFORM_CHOICES = (
    (TAK_PLATFORM_JOB, _("JOB")),
    (TAK_PLATFORM_SOPS, _("标准运维")),
    (TAK_PLATFORM_DEVOPS, _("蓝盾")),
    (TAK_PLATFORM_DEFINE, _("自定义")),
)


class TaskExecStatus(Enum):
    INIT = 0  # 初始状态
    RUNNING = 1  # 执行中
    SUCCESS = 2  # 执行成功
    FAIL = 3  # 执行失败
    SUSPENDED = 4  # 暂停
    REMOVE = 5  # 执行异常


# 任务状态中文
TASK_EXECUTE_STATUS_DICT = {
    TaskExecStatus.INIT.value: "初始状态",
    TaskExecStatus.RUNNING.value: "执行中",
    TaskExecStatus.SUCCESS.value: "执行成功",
    TaskExecStatus.FAIL.value: "执行失败",
    TaskExecStatus.SUSPENDED.value: "暂停",
    TaskExecStatus.REMOVE.value: "执行终止",
}

# 任务执行颜色
TASK_EXEC_STATUS_COLOR_DICT = {
    TaskExecStatus.INIT.value: "#B0BEC5",
    TaskExecStatus.RUNNING.value: "#4FC3F7",
    TaskExecStatus.SUCCESS.value: "#00FF00",
    TaskExecStatus.FAIL.value: "#E53935",
    TaskExecStatus.SUSPENDED.value: "#FFEE58",
    TaskExecStatus.REMOVE.value: "#E53935",
}


class PlatformType(Enum):
    """
    平台类型
    """

    DEFAULT = 0  # 默认
    JOB = 1  # 作业平台
    SOPS = 2  # 标准运维
    DEV_OPS = 3  # 蓝盾
    DEFINE = 4  # 自定义


# 定时任务
UPDATE_TASK_TIME = 60  # 更新任务时间间隔
UPDATE_TASK_MAX_WORKERS = 10  # 最大线程
UPDATE_TASK_MAX_TIME = 60 * 60 * 2  # 任务保留时间
UPDATE_TASK_LOG = "task_log"
UPDATE_TASK_PREFIX = "task_log_"  # 任务redis key前缀
TASK_NOTICE_PREFIX = "task_notice"  # 机器人日志通知前缀

# 环境变量获取
JOB_HOST = os.getenv("BKAPP_JOB_HOST", "")
if JOB_HOST == "":
    raise ValueError("BKAPP_JOB_HOST can't be empty")
DEVOPS_HOST = os.getenv("BKAPP_DEVOPS_HOST", "")
if DEVOPS_HOST == "":
    raise ValueError("BKAPP_DEVOPS_HOST can't be empty")
# ITSM相关的

PLUGIN_ITSM_SERVICE_ID = os.getenv("PLUGIN_ITSM_SERVICE_ID")
PLUGIN_ITSM_CALLBACK_URI = os.getenv("PLUGIN_ITSM_CALLBACK_URI")
PLUGIN_RELOAD_URI = os.getenv("PLUGIN_RELOAD_URI")  # 机器人reload地址
PROD_BOT_NAME = os.getenv("PROD_BOT_NAME")  # 正式环境机器人名称
STAG_BOT_NAME = os.getenv("STAG_BOT_NAME")  # 测试环境机器人名称
TIMER_USER_NAME = os.getenv("TIMER_USER_NAME")  # 定时任务执行人员
TIMER_BIZ_ID = os.getenv("TIMER_BIZ_ID")  # 定时任务执行ID
TIMER_JOB_PLAN_ID = os.getenv("TIMER_JOB_PLAN_ID")  # 定时任务执行人员
TIMER_MAX_NUM = os.getenv("TIMER_MAX_NUM", 5)  # 单业务添加的最大定时任务数量

YOUTI_TEMPLATE_ID = os.getenv("YOUTI_TEMPLATE_ID")  # 游梯模板id
MINI_PROGRAM_APPID = os.getenv("MINI_PROGRAM_APPID")  # 小程序id
