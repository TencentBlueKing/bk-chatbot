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
from src.manager.module_notice.constants import CUSTOM
from src.manager.handler.api.bk_chat import BkChatFeature
from src.manager.module_biz.handlers.biz_cache import get_biz_info
from src.manager.module_notice.handler.notice_cache import get_notice_group_data


class Notice:
    def __init__(self, im_type, msg_type, msg_content, receiver, headers, **kwargs):
        self.im_type = im_type.upper()
        self.msg_type = msg_type
        self.msg_content = msg_content
        self.receiver = receiver
        self.headers = headers
        self.kwargs = kwargs

    def send_origin_msg(self, msg_param):
        params = {
            "im": self.im_type,
            "msg_type": self.msg_type,
            "msg_param": msg_param,
            "receiver": self.receiver,
            "headers": self.headers,
        }
        biz_id = self.kwargs.get("biz_id")
        biz_info = get_biz_info(biz_id)
        send_data = {
            "biz_name": biz_info.get("bk_biz_name"),
            "biz_id": biz_id,
            "msg_source": self.kwargs.get("msg_source"),
            "msg_data": params,
            "msg_type": self.msg_type,
            "msg_context": self.msg_content,
            "im_platform": self.kwargs.get("im_platform"),
            "group_name": self.kwargs.get("group_name"),
            "raw_data": {},
        }
        _, send_result = BkChatFeature.send_msg_and_report(send_data)
        if send_result["code"] != 0:
            return {"result": False, "message": send_result["message"]}

        return {"result": True, "message": "OK"}

    def send(self):
        params = {
            "im": self.im_type,
            "msg_type": self.msg_type,
            "msg_param": {"content": self.msg_content},
            "receiver": self.receiver,
            "headers": self.headers,
            **self._extra_params,
        }
        biz_id = self.kwargs.get("biz_id")
        biz_info = get_biz_info(biz_id)
        send_data = {
            "biz_name": biz_info.get("bk_biz_name"),
            "biz_id": biz_id,
            "msg_source": self.kwargs.get("msg_source"),
            "msg_data": params,
            "msg_type": self.msg_type,
            "msg_context": self.msg_content,
            "im_platform": self.kwargs.get("im_platform"),
            "group_name": self.kwargs.get("group_name"),
            "raw_data": {},
        }
        _, send_result = BkChatFeature.send_msg_and_report(send_data)
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

        # 支持QQ的告警类型
        if self.im_type in ["QQ"]:
            params = {
                "msg_type": "0",
                "msg_param": {
                    "content": [{"data": self.msg_content}],
                },
            }

        # 支持飞书
        if self.im_type in ["LARK_WEBHOOK"]:
            params = {
                "msg_type": "post",
                "msg_param": {
                    "post": {
                        "zh-CN": {
                            "title": "",
                            "content": [[{"tag": "text", "text": self.msg_content}]],
                        }
                    }
                },
            }

        # 支持钉钉
        if self.im_type in ["DING_WEBHOOK"]:
            params = {
                "msg_type": "text",
                "msg_param": {"content": self.msg_content},
            }

        # 支持微信公众号
        if self.im_type in ["MINI_PROGRAM"]:
            params = {
                "msg_type": "mini",
                "msg_param": {
                    "first": {"value": self.msg_content},
                    "keynote1": {"value": "     -"},
                    "keynote2": {"value": "     -"},
                },
            }

        # 支持邮件
        if self.im_type in ["EMAIL"]:
            params = {
                "msg_param": {"title": self.kwargs.get("group_name", "BkChat消息通知"), "content": self.msg_content},
            }

        return params


def send_msg_to_notice_group(group_id_list, msg_type, msg_content, msg_param={}, custom_headers={}):
    notice_groups = get_notice_group_data(group_id_list)
    send_success = True
    fail_message_list = []
    fail_notice_group_id_list = []
    for notice_group in notice_groups:
        kwargs = {
            "im_platform": notice_group.get("im_platform"),
            "biz_id": notice_group.get("biz_id"),
            "msg_source": CUSTOM,
            "group_name": notice_group.get("notice_group_name"),
        }
        headers = notice_group.get("headers")
        headers.update(custom_headers)
        notice = Notice(
            notice_group.get("im"),
            msg_type,
            msg_content,
            notice_group.get("receiver"),
            headers,
            **kwargs,
        )
        if msg_param:
            send_result = notice.send_origin_msg(msg_param)
        else:
            send_result = notice.send()
        if not send_result["result"]:
            send_success = False
            fail_notice_group_id_list.append(notice_group["notice_group"])
            fail_message_list.append(
                f"[NoticeGroup-{notice_group['notice_group']}] send msg failed,error is {send_result['message']}"
            )

    return {
        "result": send_success,
        "message": "\n".join(fail_message_list),
        "fail_notice_group_id_list": fail_notice_group_id_list,
    }
