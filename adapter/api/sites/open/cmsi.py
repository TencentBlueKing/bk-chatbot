# -*- coding: utf-8 -*-

from adapter.common.log import logger
from adapter.api.base import DataAPI
from adapter.api.modules.utils import add_esb_info_before_request


def before_send_cmsi_api(params):
    receivers = params.pop("receivers", [])
    if "receiver__username" not in params:
        if isinstance(receivers, list):
            params["receiver__username"] = ",".join(receivers)
        elif isinstance(receivers, str):
            params["receiver__username"] = receivers
    return add_esb_info_before_request(params)


def before_send_cmsi_sms(params):
    params = before_send_cmsi_api(params)
    if "message" in params and "content" not in params:
        params["content"] = params["message"]
    return add_esb_info_before_request(params)


def before_send_cmsi_wechat(params):
    params = before_send_cmsi_api(params)
    if "message" in params:
        params["data"] = {
            "message": params.pop("message", ""),
            "heading": params.pop("title", "") or params.pop("heading", ""),
        }
    return add_esb_info_before_request(params)


def before_send_cmsi_voice_msg(params):
    params = before_send_cmsi_api(params)
    if "message" in params:
        params["auto_read_message"] = params["message"]
    return add_esb_info_before_request(params)


class _CmsiApi(object):
    def __init__(self):
        try:
            from config.domains import CMSI_API_ROOT

            self.get_msg_type = DataAPI(
                method="POST",
                url=CMSI_API_ROOT + "get_msg_type/",
                module="TOF",
                description="支持发送消息的类型",
                before_request=before_send_cmsi_api,
            )
            self.send_mail = DataAPI(
                method="POST",
                url=CMSI_API_ROOT + "send_mail/",
                module="CMSI",
                description="发送邮件",
                before_request=before_send_cmsi_api,
            )
            self.send_sms = DataAPI(
                method="POST",
                url=CMSI_API_ROOT + "send_sms/",
                module="CMSI",
                description="发送短信通知",
                before_request=before_send_cmsi_sms,
            )
            self.send_wechat = DataAPI(
                method="POST",
                url=CMSI_API_ROOT + "send_weixin/",
                module="CMSI",
                description="发送微信通知",
                before_request=before_send_cmsi_wechat,
            )
        except ImportError:
            logger.error("无法在配置文件中找到CMSI_API_ROOT")


CmsiApi = _CmsiApi()
