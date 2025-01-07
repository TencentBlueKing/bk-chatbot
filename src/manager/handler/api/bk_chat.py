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
import re
import json
import logging
import requests
from typing import Any

from django.conf import settings

from adapter.api import BkChatApi
from common.utils.my_time import mk_now_time

logger = logging.getLogger("root")


def check_wecom_group(text):
    pattern = r"ww\d+"
    result = re.search(pattern, text)
    if result:
        return True
    else:
        return False


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

    @classmethod
    def msg_push(cls, topic, key, value):
        """
        数据上报
        @param topic:
        @param key:
        @param value:
        @return:
        """
        params = {
            "topic": topic,
            "key": key,
            "value": value,
        }
        return BkChatApi.msg_push(params=params)

    @classmethod
    def file_send_service(cls, receiver_list, file_name, image_base64, msg_type="image"):
        """
        发送文件(新)
        @return:
        """
        url = settings.BK_CHAT_APIGW + "plugin/api/rest/file/send/"
        single_receiver_list = [r for r in receiver_list if not check_wecom_group(r)]
        group_receiver_list = [r for r in receiver_list if check_wecom_group(r)]

        headers = {
            "Content-Type": "application/json",
            "X-Bkapi-Authorization": json.dumps(
                {
                    "bk_app_code": settings.APP_CODE,
                    "bk_app_secret": settings.SECRET_KEY,
                }
            ),
        }

        data = {
            "file_name": file_name,
            "im_type": "WEWORK",
            "msg_type": msg_type,
            "buff": image_base64,
        }
        if single_receiver_list:
            data.update(
                {
                    "receiver": {
                        "receiver_type": "single",
                        "receiver_ids": single_receiver_list,
                    },
                }
            )
            result = requests.post(url, json=data, headers=headers).json()
            if not result["result"]:
                logger.error(result)

        if group_receiver_list:
            data.update(
                {
                    "receiver": {
                        "receiver_type": "group",
                        "receiver_ids": group_receiver_list,
                    },
                }
            )
            result = requests.post(url, json=data, headers=headers).json()
            if not result["result"]:
                logger.error(result)


class BkChatFeature(BkChat):
    @classmethod
    def send_msg_and_report(cls, data):
        """
        {
            "biz_name": "string",    # 业务名称
            "biz_id": int,           # 业务id
            "msg_source": "string",  # 消息来源 alarm、custom、broadcast
            "msg_data": dict,        # 消息数据
            "msg_context": "string", # 消息内容(用于页面展示)
            "im_platform": "string", # 平台
            "group_name": "string",  # 群组名称
            "raw_data": dict,        # 原始数据
        }
        """
        msg_data = data.get("msg_data", {})
        # 消息发送
        ret_send_msg = cls.new_send_msg(**msg_data)
        # 值设置
        data.setdefault("send_time", mk_now_time())  # 设置发送时间
        data.setdefault("send_result", ret_send_msg.get("code") == 0)  # 设置发送结果
        data.setdefault("msg_type", "text")  # 设置消息类型
        data.setdefault("im_type", msg_data.get("im"))  # 设置IM类型
        # 如果不存在raw则设置为msg_context
        if len(data.get("raw_data", {}).keys()) == 0:
            data["raw_data"] = {"msg_context": data.get("msg_context")}

        topic = data.get("topic", "bkchat_saas")  # 获取topic
        key = data.get("kafka_key", "bkchat")  # 获取key
        ret_reported = cls.msg_push(topic, key, json.dumps(data))
        return ret_reported, ret_send_msg
