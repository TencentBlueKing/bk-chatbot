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

Default configurations.

Any derived configurations must import everything from this module
at the very beginning of their code, and then set their own value
to override the default one.

For example:

>>> from opsbot.default_config import *
>>> PORT = 9090
>>> DEBUG = False
>>> SUPERUSERS.add(123456)
>>> NICKNAME = 'SAB'
"""

from datetime import timedelta
from typing import Container, Union, Iterable, Pattern, Optional, Dict, Any

from .self_typing import Expression_T

API_ROOT: str = 'https://qyapi.weixin.qq.com/cgi-bin'
ACCESS_TOKEN: str = ''
SECRET: str = ''
HOST: str = '127.0.0.1'
PORT: int = 8080
DEBUG: bool = True

SUPERUSERS: Container[int] = set()
NICKNAME: Union[str, Iterable[str]] = ''
RTX_NAME: str = ''

COMMAND_START: Iterable[Union[str, Pattern]] = {'/', '!', '／', '！'}
COMMAND_SEP: Iterable[Union[str, Pattern]] = {'/', '.'}

SESSION_EXPIRE_TIMEOUT: Optional[timedelta] = timedelta(minutes=3)
SESSION_RUN_TIMEOUT: Optional[timedelta] = None
SESSION_RUNNING_EXPRESSION: Expression_T = '您有命令正在执行，请稍后再试'

SHORT_MESSAGE_MAX_LENGTH: int = 50
NLP_CONFIDENCE: float = 60.0

DEFAULT_VALIDATION_FAILURE_EXPRESSION: Expression_T = '您的输入不符合要求，请重新输入'
MAX_VALIDATION_FAILURES: int = 3
TOO_MANY_VALIDATION_FAILURES_EXPRESSION: Expression_T = \
    '您输入错误太多次啦，如需重试，请重新触发本功能'

SESSION_CANCEL_EXPRESSION: Expression_T = '好的'

APSCHEDULER_CONFIG: Dict[str, Any] = {
    'apscheduler.timezone': 'Asia/Shanghai'
}
