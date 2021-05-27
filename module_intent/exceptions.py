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
from django.utils.translation import ugettext as _

from common import exceptions


class BaseModuleIntentException(exceptions.BaseException):
    """
    业务模块异常
    """

    MODULE_CODE = exceptions.ErrorCode.SYS_MODULE_BIZ
    MESSAGE: str = _("意图模块异常")


class IntentReloadDaemonException(BaseModuleIntentException):
    """
    查询业务失败
    """

    def __init__(self, error_message: str):
        self.MESSAGE: str = error_message
        self.ERROR_CODE: str = "000"
        super().__init__()
