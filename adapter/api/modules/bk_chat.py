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

from adapter.api.base import BaseApi, ProxyDataAPI


class _BkChatApi(BaseApi):
    MODULE = _("BKCHAT")

    def __init__(self):
        self.handle_scheduler = ProxyDataAPI(_("回调机器人"))
        self.send_msg = ProxyDataAPI(_("发送消息"))
        self.corpus_intent_create = ProxyDataAPI(_("语料意图添加"))
        self.send_msg_v3 = ProxyDataAPI(_("发送消息(新)"))
        self.send_broadcast = ProxyDataAPI(_("发送消息(新)"))


BkChatApi = _BkChatApi()
