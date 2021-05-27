# -*- coding: utf-8 -*-
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
