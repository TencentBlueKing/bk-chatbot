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

from enum import Enum

from django.utils.translation import ugettext_lazy as _

from common.utils.os import get_env_or_raise

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


class IntentMatchPattern(Enum):
    LIKE = 1  # 相似度匹配
    EXACT = 2  # 完全匹配


TASK_EXECUTE_STATUS_DICT = {
    TaskExecStatus.INIT.value: "未执行",
    TaskExecStatus.RUNNING.value: "执行中",
    TaskExecStatus.SUCCESS.value: "执行成功",
    TaskExecStatus.FAIL.value: "执行失败",
    TaskExecStatus.SUSPENDED.value: "暂停",
    TaskExecStatus.REMOVE.value: "执行终止",
}

# 任务执行颜色
TASK_EXEC_STATUS_COLOR_DICT = {
    TaskExecStatus.INIT.value: "#B0BEC5",
    TaskExecStatus.RUNNING.value: "#fd9e31",
    TaskExecStatus.SUCCESS.value: "#3dca63",
    TaskExecStatus.FAIL.value: "#E53935",
    TaskExecStatus.SUSPENDED.value: "#FFEE58",
    TaskExecStatus.REMOVE.value: "#E53935",
}

# 标准运维网关节点类型
SOPS_GATEWAY_NODE_TYPE_MAP = {
    "ExclusiveGateway": "分支网关",
    "ParallelGateway": "并行网关",
    "ConditionalParallelGateway": "条件并行网关",
    "ConvergeGateway": "汇聚网关",
}
# 环境变量获取
JOB_HOST = get_env_or_raise("BKAPP_JOB_HOST")
DEVOPS_HOST = get_env_or_raise("BKAPP_DEVOPS_HOST")

# 用户相关
USER_VISIT = "USER_VISIT"

MAX_WORKER = 10  # 多线程执行最大线程数

BKCHAT_CACHE_PREFIX = get_env_or_raise("BKCHAT_CACHE_PREFIX", "bkchat")
