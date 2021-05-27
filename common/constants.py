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

from django.utils.translation import ugettext_lazy as _

# 机器人类型
CHAT_BOT_TYPE_WEWORK = "xwork"
CHAT_BOT_TYPE_QQ = "qq"
CHAT_BOT_TYPE_WX = "wechat"
CHAT_BOT_TYPE_SLACK = "slack"
CHAT_BOT_TYPE_DEFAULT = "default"

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
# 任务状态
TASK_EXECUTE_STATUS_CHOICES = (
    ("0", _("初始状态")),
    ("1", _("执行中")),
    ("2", _("执行成功")),
    ("3", _("执行失败")),
    ("4", _("执行暂停")),
    ("5", _("异常|终止")),
)
