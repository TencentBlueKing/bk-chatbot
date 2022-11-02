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

from blueapps.utils.logger import logger_celery as logger

from common.design.strategy import Strategy
from common.utils.os import get_env_or_raise
from common.utils.str import check_reg
from src.manager.handler.api.bk_chat import BkChat
from src.manager.module_intent.constants import TASK_EXEC_STATUS_COLOR_DICT, TASK_EXECUTE_STATUS_DICT

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

        try:
            # 获取参数
            params = cls._map.value[notice_type](**data)
            ret = BkChat.new_send_msg(**params)
            logger.info(ret)
        except Exception:
            logger.exception("消息发送错误")


@Message.register(Message.RTX.value)
def get_wecom_params(
    bot_name: str, user: str, receiver: str, intent_name: str, task_uri: str, status: str, param_list: list, **kwargs
):
    """
    wecom推送参数
    :param bot_name:     机器人名称
    :param user:         发起对话的用户
    :param receiver:     接收人或者群
    :param intent_name:  意图名称
    :param task_uri:     任务链接
    :param status:       任务状态
    :param param_list:   参数列表
    :param color:
    :param kwargs:
    :return:
    """
    # md拼接
    ch_status = TASK_EXECUTE_STATUS_DICT.get(status)  # 获取中文状态
    color = TASK_EXEC_STATUS_COLOR_DICT.get(status)  # 获取md颜色
    md = f"""<font color="#E53935">{user}</font>您好！"""
    md += f"""您的任务[[{intent_name}]({task_uri})]<font color="{color}">{ch_status}</font>\n"""
    if len(param_list) > 0:
        md += "**参数列表**\n"
    for param in param_list:
        name = param.get("name")
        value = param.get("value")
        if value == "":
            value = "无数据"
        md += f"""<font color="#858585">  {name}</font>：{value} \n"""
    md += f"如需查看任务详情，请点击：[任务详情]({task_uri})"
    data = {
        "im": "WEWORK",
        "msg_type": "markdown",
        "msg_param": {"content": md},
        "receiver": {
            "receiver_type": "group" if check_reg("ww[0-9]+", receiver) else "single",
            "receiver_ids": [receiver],
        },
        "headers": {},
    }

    # 获取bot_code 获取失败使用默认的bot发送
    robot_code = os.getenv(f"{bot_name}_CODE")
    if robot_code:
        data["headers"].update(
            **{
                "APP-SECRET": robot_code,
            }
        )
    return data


@Message.register(Message.YOU_TI.value)
def get_wx_params(
    log_id: int, user: str, receiver: str, intent_name: str, intent_id: int, time: str, status: str, **kwargs
):
    """
    小程序推送
    :param log_id:      日志id
    :param user:        用户
    :param receiver:    接收人open_id
    :param intent_name: 意图名称
    :param intent_id:   意图ID
    :param time:        时间
    :param status:      状态
    :param kwargs:
    :return:
    """
    ch_status = TASK_EXECUTE_STATUS_DICT.get(status)  # 获取中文状态
    data = {
        "im": "MINI_PROGRAM",
        "msg_type": "mini",
        "msg_param": {
            "first": {"value": f"{user}，您的任务{ch_status}!", "color": "#red"},
            "keynote1": {"value": f"{intent_name}", "color": "#173177"},
            "keynote2": {"value": str(time), "color": "#173177"},
            "remark": {"value": "游梯研运助手7*24为您服务!", "color": "#173177"},
        },
        "receiver": {
            "receiver_type": "single",
            "receiver_ids": [receiver],
        },
        "headers": {
            "MINI-PROGRAM-PATH": f"pages/taskinfo/taskinfo?id={log_id}&intent_id={intent_id}",
            "MINI-PROGRAM-APP-ID": MINI_PROGRAM_APPID,
            "MINI-PROGRAM-TEMPLATE-ID": YOUTI_TEMPLATE_ID,
        },
    }
    return data
