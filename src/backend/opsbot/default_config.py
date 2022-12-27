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

"""
Default configurations.

Any derived configurations must import everything from this module
at the very beginning of their code, and then set their own value
to override the default one.

For example:

>>> from opsbot.default_config import *
>>> PORT = 9090
>>> DEBUG = False
>>> SUPERUSERS.add(123456)
>>> NICKNAME = 'SB'
"""

import os
from datetime import timedelta
from typing import Container, Union, Iterable, Pattern, Optional, Dict, Any

from .self_typing import Expression_T

API_ROOT: str = os.getenv('API_ROOT', '')
ACCESS_TOKEN: str = ''
SECRET: str = ''
HOST: str = os.getenv('HOST', '127.0.0.1')
PORT: int = os.getenv('PORT', 8080)
DEBUG: bool = True

SUPERUSERS: Container[int] = set(os.getenv('SUPERUSERS', '').split(','))
NICKNAME: Union[str, Iterable[str]] = os.getenv('NICKNAME', '')
RTX_NAME: str = os.getenv('RTX_NAME', '')
ID: str = os.getenv('ID', '')

COMMAND_START: Iterable[Union[str, Pattern]] = os.getenv('COMMAND_START', {''}) or {'/', '!', '／', '！'}
COMMAND_SEP: Iterable[Union[str, Pattern]] = {'/', '.'}

SESSION_EXPIRE_TIMEOUT: Optional[timedelta] = timedelta(minutes=3)
SESSION_RUN_TIMEOUT: Optional[timedelta] = None
SESSION_RUNNING_EXPRESSION: Expression_T = '您有命令正在执行，请稍后再试'

SHORT_MESSAGE_MAX_LENGTH: int = 1024
NLP_CONFIDENCE: float = 60.0

DEFAULT_VALIDATION_FAILURE_EXPRESSION: Expression_T = '您的输入不符合要求，请重新输入'
MAX_VALIDATION_FAILURES: int = 3
TOO_MANY_VALIDATION_FAILURES_EXPRESSION: Expression_T = \
    '您输入错误太多次啦，如需重试，请重新触发本功能'

SESSION_CANCEL_EXPRESSION: Expression_T = '好的'

APSCHEDULER_CONFIG: Dict[str, Any] = {
    'apscheduler.timezone': 'Asia/Shanghai'
}

SESSION_RESERVED_WORD: Iterable[str] = [
    'bk_chat_group_id',
    'bk_chat_welcome',
    'bk_cc_biz_bind',
    'bk_cc_biz_select',
    'bk_chat_stat_execution',
    'bk_chat_search_knowledge',
    'bk_chat_task_delete_scheduler',
    'bk_chat_task_callback',
    'bk_chat_task_execute',
    'bk_chat_task_list',
    'bk_app_task_select',
    'bk_app_task_filter',
    'bk_shortcut_create',
    'bk_shortcut_execute',
    'bk_shortcut_list',
    'bk_shortcut_delete',
    'bk_job_plan_list',
    'bk_job_plan_search',
    'bk_job_plan_select',
    'bk_job_plan_execute',
    'bk_job_plan_update',
    'bk_job_plan_cancel',
    'bk_sops_template_list',
    'bk_sops_template_select',
    'bk_sops_template_execute',
    'bk_sops_template_update',
    'bk_sops_template_cancel',
    'bk_devops_project_list',
    'bk_devops_project_select',
    'bk_devops_pipeline_select',
    'bk_devops_pipeline_update',
    'bk_devops_pipeline_execute',
    'bk_devops_pipeline_cancel',
    'bk_itsm',
    'bk_itsm_select_service'
]
SESSION_RESERVED_CMD: Iterable[str] = os.getenv('SESSION_RESERVED_CMD', '').split(',')
IS_USE_SESSION_WHITELIST: bool = os.getenv('IS_USE_SESSION_WHITELIST', True)
IS_USE_I18N: bool = os.getenv('IS_I18N', False)
