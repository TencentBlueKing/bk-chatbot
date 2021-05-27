# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


class ConfFixture(object):
    COMMUNITY_PAAS_HOST = ''
    COMMUNITY_QCLOUD_LOGIN_HOST = ''
    BACKEND_TYPE = 'qcloud_ptlogin'
    USER_BACKEND = 'qcloud_ptlogin.backends.QPtloginBackend'
    LOGIN_REQUIRED_MIDDLEWARE = ('qcloud_ptlogin.middlewares.'
                                 'LoginRequiredMiddleware')
    USER_MODEL = 'qcloud_ptlogin.models.UserProxy'

    CONSOLE_LOGIN_URL = f'http://{COMMUNITY_PAAS_HOST}/accounts/login_page/'
    LOGIN_URL = f'http://{COMMUNITY_QCLOUD_LOGIN_HOST}'
    LOGIN_PLAIN_URL = f'http://{COMMUNITY_QCLOUD_LOGIN_HOST}/plain/'
    ADD_CROSS_PREFIX = True
    ADD_APP_CODE = True

    IFRAME_HEIGHT = 390
    IFRAME_WIDTH = 670

    WEIXIN_BACKEND_TYPE = 'null'
    WEIXIN_MIDDLEWARE = 'null.NullMiddleware'
    WEIXIN_BACKEND = 'null.NullBackend'

    SMS_CLIENT_MODULE = 'cmsi'
    SMS_CLIENT_FUNC = 'send_sms'
    SMS_CLIENT_USER_ARGS_NAME = 'receiver__uin'
    SMS_CLIENT_CONTENT_ARGS_NAME = 'content'

    RIO_BACKEND_TYPE = 'null'
    RIO_MIDDLEWARE = 'null.NullMiddleware'
    RIO_BACKEND = 'null.NullBackend'

    BK_JWT_MIDDLEWARE = 'null.NullMiddleware'
    BK_JWT_BACKEND = 'null.NullBackend'
