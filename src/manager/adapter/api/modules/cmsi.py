# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from ..base import ProxyDataAPI, BaseApi


class _CmsiApi(BaseApi):
    MODULE = _("CMSI")

    def __init__(self):
        self.send_mail = ProxyDataAPI("发送邮件")
        self.send_sms = ProxyDataAPI("发送短信")
        self.send_wechat = ProxyDataAPI("发送微信消息")
        self.send_eewechat = ProxyDataAPI("发送企业微信消息")
        self.get_msg_type = ProxyDataAPI("支持发送消息的类型")


CmsiApi = _CmsiApi()
