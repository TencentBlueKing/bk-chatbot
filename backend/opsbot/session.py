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

from . import OpsBot
from .helpers import send
from .self_typing import Context_T, Message_T


class BaseSession:
    __slots__ = ('bot', 'ctx')

    def __init__(self, bot: OpsBot, ctx: Context_T):
        self.bot = bot
        self.ctx = ctx

    @property
    def self_id(self) -> int:
        return self.bot.config.RTX_NAME

    async def send(self, message: Message_T, *,
                   at_sender: bool = False,
                   ensure_private: bool = False,
                   ignore_failure: bool = True,
                   **kwargs) -> None:
        """
        Send a message ignoring failure by default.

        :param message: message to send
        :param at_sender: @ the sender if in group or discuss chat
        :param ensure_private: ensure the message is sent to private chat
        :param ignore_failure: if any CQHttpError raised, ignore it
        :return: the result returned by CQHTTP
        """
        return await send(self.bot, self.ctx, message,
                          at_sender=at_sender,
                          ensure_private=ensure_private,
                          ignore_failure=ignore_failure, **kwargs)
