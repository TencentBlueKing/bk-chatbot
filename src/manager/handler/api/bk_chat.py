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


def set_im_headers(params):
    """
    自定设置headers
    @param params:
    @return:
    """
    headers = params.get("headers")
    return headers


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

    @classmethod
    def corpus_intent_create(cls, domain_id, intent_key, intent_name, slots):
        """
        语料添加
        @param domain_id:   领域ID
        @param intent_key:  意图key
        @param intent_name: 意图名称
        @param slots:       插槽
        @return:
        """
        params = {
            "domain_id": domain_id,
            "intent_key": intent_key,
            "intent_name": intent_name,
            "slots": slots,
        }
        return BkChatApi.corpus_intent_create(params=params, raw=True)

    @classmethod
    def new_send_msg(cls, im, msg_type, msg_param, receiver, headers: dict):
        """
        发送消息(新)
        @param im:
        @param msg_type:
        @param msg_param:
        @param receiver:
        @param headers:
        @return:
        """
        params = {
            "im": im,
            "msg_type": msg_type,
            "msg_param": msg_param,
            "receiver": receiver,
            "headers": headers,
        }
        return BkChatApi.send_msg_v3(params=params, headers=set_im_headers, raw=True)

    @classmethod
    def send_broadcast(cls, broadcast_body):
        """
        推送任务实时播报
        @param broadcast_body: 播报内容结构体
        @return:
        """
        params = {**broadcast_body}
        return BkChatApi.send_broadcast(params=params, raw=True)
