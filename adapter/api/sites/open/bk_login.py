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

from adapter.api.base import DataAPI
from adapter.api.modules.utils import add_esb_info_before_request
from config.domains import BK_LOGIN_APIGATEWAY_ROOT


class _BKLoginApi(object):
    MODULE = _("PaaS平台登录模块")

    def __init__(self):
        self.get_all_user = DataAPI(
            method="POST",
            url=BK_LOGIN_APIGATEWAY_ROOT + "get_all_user/",
            module=self.MODULE,
            description="获取所有用户",
            before_request=add_esb_info_before_request,
            cache_time=300,
        )
        self.get_user = DataAPI(
            method="POST",
            url=BK_LOGIN_APIGATEWAY_ROOT + "get_user/",
            module=self.MODULE,
            description="获取单个用户",
            before_request=add_esb_info_before_request,
        )


BKLoginApi = _BKLoginApi()
