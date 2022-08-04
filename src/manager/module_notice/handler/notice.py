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
from src.manager.handler.api.bk_chat import BkChat
from src.manager.module_notice.handler.notice_cache import get_notice_group_data


class Notice:
    def __init__(self, im_type, msg_type, msg_content, receiver, headers):
        self.im_type = im_type.upper()
        self.msg_type = msg_type
        self.msg_content = msg_content
        self.receiver = receiver
        self.headers = headers

    def send(self):
        params = {
            "im": self.im_type,
            "msg_type": self.msg_type,
            "msg_param": {"content": self.msg_content},
            "receiver": self.receiver,
            "headers": self.headers,
            **self._extra_params,
        }

        send_result = BkChat.new_send_msg(**params)

        if send_result["code"] != 0:
            return {"result": False, "message": send_result["message"]}

        return {"result": True, "message": "OK"}

    @property
    def _extra_params(self):
        params = {}
        if self.im_type in ["SLACK", "SLACK_WEBHOOK"]:
            params = {
                "msg_type": "text",
                "msg_param": {"text": self.msg_content},
            }

        return params


def send_msg_to_notice_group(group_id_list, msg_type, msg_content):
    notice_groups = get_notice_group_data(group_id_list)
    for notice_group in notice_groups:
        notice = Notice(
            notice_group.get("im"), msg_type, msg_content, notice_group.get("receiver"), notice_group.get("headers")
        )
        send_result = notice.send()
        if not send_result["result"]:
            return send_result

    return {"result": True, "message": "OK"}
