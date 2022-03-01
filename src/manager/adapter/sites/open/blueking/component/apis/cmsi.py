# -*- coding: utf-8 -*-
from ..base import ComponentAPI


class CollectionsCMSI(object):
    """Collections of CMSI APIS"""

    def __init__(self, client):
        self.client = client

        self.get_msg_type = ComponentAPI(
            client=self.client,
            method='GET',
            path='/api/c/compapi{bk_api_ver}/cmsi/get_msg_type/',
            description='查询消息发送类型',
        )
        self.send_mail = ComponentAPI(
            client=self.client, method='POST', path='/api/c/compapi{bk_api_ver}/cmsi/send_mail/', description='发送邮件'
        )
        self.send_mp_weixin = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/cmsi/send_mp_weixin/',
            description='发送公众号微信消息',
        )
        self.send_msg = ComponentAPI(
            client=self.client, method='POST', path='/api/c/compapi{bk_api_ver}/cmsi/send_msg/', description='通用消息发送'
        )
        self.send_qy_weixin = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/cmsi/send_qy_weixin/',
            description='发送企业微信',
        )
        self.send_sms = ComponentAPI(
            client=self.client, method='POST', path='/api/c/compapi{bk_api_ver}/cmsi/send_sms/', description='发送短信'
        )
        self.send_voice_msg = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/cmsi/send_voice_msg/',
            description='公共语音通知',
        )
        self.send_weixin = ComponentAPI(
            client=self.client,
            method='POST',
            path='/api/c/compapi{bk_api_ver}/cmsi/send_weixin/',
            description='发送微信消息',
        )
