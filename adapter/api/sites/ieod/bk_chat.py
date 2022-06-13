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

from adapter.api.base import DataAPI
from adapter.sites.ieod.config.domains import BK_CHAT_APIGW


class _BkChatApi:
    MODULE = _("BKCHAT")

    @property
    def handle_scheduler(self):
        return DataAPI(
            method="POST",
            url=BK_CHAT_APIGW + "api/v1/base/handle_scheduler/",
            description=_("执行回调接口"),
            module=self.MODULE,
        )

    @property
    def send_msg(self):
        return DataAPI(
            method="POST",
            url=BK_CHAT_APIGW + "api/v1/bkchat/send_msg/",
            description=_("发送消息"),
            module=self.MODULE,
        )

    @property
    def corpus_create(self):
        return DataAPI(
            method="POST",
            url=BK_CHAT_APIGW + "api/v1/corpus/manage/",
            description=_("语料添加"),
            module=self.MODULE,
        )


BkChatApi = _BkChatApi()
