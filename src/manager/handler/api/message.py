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

import os

import requests
from blueapps.utils.logger import logger_celery as logger

from common.design.strategy import Strategy
from common.utils.os import get_env_or_raise
from src.manager.handler.in_api.youti_api import MgaAPI

# 消息通知相关
YOUTI_TEMPLATE_ID = get_env_or_raise("YOUTI_TEMPLATE_ID")  # 游梯模板id
MINI_PROGRAM_APPID = get_env_or_raise("MINI_PROGRAM_APPID")  # 小程序id


class Message(Strategy):
    """
    企业微信通知
    """

    RTX = 1
    YOU_TI = 2

    _map = dict()

    @classmethod
    def notice(cls, **data):
        # 长度大于28则是外部开发商的账号
        receiver = data.get("receiver")
        if len(receiver) < 28:
            notice_type = cls.RTX.value
        else:
            notice_type = cls.YOU_TI.value
        return cls._map.value[notice_type](**data)


def call(uri: str, method: str, **params):
    """
    请求数据
    @param uri:
    @param method:
    @param params:
    @return:
    """
    response = getattr(requests, method)(uri, **params)
    logger.info(response.text)
    return response.json()


@Message.register(Message.RTX.value)
def rtx_notice(
    bot_name: str,
    user: str,
    receiver: str,
    intent_name: str,
    task_uri: str,
    status: str,
    param_list: list,
    color: str,
    **kwargs,
):
    """
    发送rtx信息
    """
    bot_host = os.getenv(f"{bot_name}_MSG_URI")
    host = bot_host if bot_host else os.getenv("WE_COM_MSG_URI")

    md = f"""<font color="#29B6F6">{user} </font>您好！"""
    md += f"""您的任务<font color="#29B6F6">  {intent_name}</font> <font color="{color}">{status}</font>\n"""
    if len(param_list) > 0:
        md += ">**参数列表**\n"
    for param in param_list:
        name = param.get("name")
        value = param.get("value")
        if value == "":
            value = "无数据"
        md += f""" > <font color="#FFA000">  {name}</font>：{value} \n"""

    md += f">  如需查看任务详情，请点击：[任务详情]({task_uri})"

    data = {
        "username": receiver,
        "markdown": md,
    }
    return call(f"{host}/sendByName", "post", json=data)


@Message.register(Message.YOU_TI.value)
def youti_notice(
    log_id: int, user: str, receiver: str, intent_name: str, intent_id: int, time: str, status: str, **kwargs
):

    page_path = f"pages/taskinfo/taskinfo?id={log_id}&intent_id={intent_id}"
    data = {
        "openid": receiver,
        "template_id": YOUTI_TEMPLATE_ID,
        "body": {
            "first": {"value": f"{user}，您的任务{status}！", "color": "#red"},
            "keynote1": {"value": f"{intent_name}", "color": "#173177"},
            "keynote2": {"value": str(time), "color": "#173177"},
            "remark": {"value": "游梯研运助手7*24为您服务!", "color": "#173177"},
        },
        "miniprogram": {"appid": MINI_PROGRAM_APPID, "pagepath": page_path},
    }
    return MgaAPI().send_custom_msg(**data)
