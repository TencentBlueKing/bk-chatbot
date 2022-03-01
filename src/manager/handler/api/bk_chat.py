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

from typing import Any

from adapter.api import BkChatApi


class BkChat:
    @classmethod
    def handle_scheduler(cls, **params: Any) -> dict:
        """
        机器人调度器
        @param prams:
        @return:
        """

        return BkChatApi.handle_scheduler(params=params, raw=True)

    @classmethod
    def send_msg(cls, rtx: str, content: str, markdown: str):
        """
        发送消息
        @param rtx:
        @param content:
        @param markdown:
        @return:
        """
        params = {
            "username": rtx,
            "content": content,
            "markdown": markdown,
        }
        return BkChatApi.send_msg(params=params, raw=True)
