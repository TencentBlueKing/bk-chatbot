# -*- coding: utf-8 -*-

from django.conf import settings

from adapter.api.modules.utils import add_esb_info_before_request
from adapter.api.base import DataAPI
from adapter.common.log import logger


def before_send_tof_api(params):
    if "operator" not in params:
        params["operator"] = settings.APP_CODE
    receivers = params.pop("receivers", [])
    if "receiver" not in params:
        if isinstance(receivers, list):
            params["receiver"] = ",".join(receivers)
        elif isinstance(receivers, str):
            params["receiver"] = receivers

    if "title" not in params:
        params["title"] = ""
    return add_esb_info_before_request(params)


def before_send_smcs_api(params):
    if "operator" not in params:
        params["operator"] = settings.APP_ID
    receivers = params.pop("receivers", [])
    if "receiver" not in params:
        if isinstance(receivers, list):
            params["receiver"] = ",".join(receivers)
        elif isinstance(receivers, str):
            params["receiver"] = receivers
    return params


def get_cmsi_type_ieod():
    return [{"type": "mail", "label": "邮件"}, {"type": "eewechat", "label": "企业微信"}, {"type": "wechat", "label": "微信"}]


class _CmsiApi(object):
    def __init__(self):
        try:
            from config.domains import TOF_APIGATEWAY_ROOT, WECHAT_APIGATEWAY_ROOT

            self.get_msg_type = get_cmsi_type_ieod
            self.send_mail = DataAPI(
                method="POST",
                url=TOF_APIGATEWAY_ROOT + "send_mail/",
                module="TOF",
                description="发送邮件",
                before_request=before_send_tof_api,
            )
            self.send_eewechat = DataAPI(
                method="POST",
                url=TOF_APIGATEWAY_ROOT + "send_rtx/",
                module="TOF",
                description="发送企业微信",
                before_request=before_send_tof_api,
            )
            self.send_wechat = DataAPI(
                method="POST",
                url=WECHAT_APIGATEWAY_ROOT + "send_msg/",
                module="TOF",
                description="发送微信",
                before_request=before_send_tof_api,
            )
        except ImportError:
            logger.error("无法在配置文件中找到TOF_APIGATEWAY_ROOT")


CmsiApi = _CmsiApi()
