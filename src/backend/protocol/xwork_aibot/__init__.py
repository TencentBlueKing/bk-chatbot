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

from collections import namedtuple
from typing import Any, Optional, Dict


from opsbot.adapter import Bot as BaseBot
from . import config as XworkAibotConfig
from .proxy import Proxy as XworkAibotProxy
from .message import Message, MessageSegment

_message_preprocessors = set()

_min_context_fields = (
    'msg_sender_id',
)

_MinContext = namedtuple('MinContext', _min_context_fields)


class Bot(BaseBot, XworkAibotProxy):
    protocol_config: Dict = None

    def __init__(self, config_object: Optional[Any] = None):
        if config_object is None:
            from opsbot import default_config as config_object

        self.config = config_object
        self.protocol_config = {k: v for k, v in XworkAibotConfig.__dict__.items()}
        XworkAibotProxy.__init__(self, self.config.API_ROOT, self.protocol_config)
        self.asgi.debug = self.config.DEBUG

    async def call_api(self, *args, **kwargs):
        pass

    async def check_permission(self, *args, **kwargs):
        pass

    async def handle_event(self, *args, **kwargs):
        pass

    async def handle_message(self, *args, **kwargs):
        pass

    async def send(self, *args, **kwargs):
        pass

    @property
    def type(self) -> str:
        return "xwork_aibot"