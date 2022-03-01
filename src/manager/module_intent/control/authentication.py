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
import json
import os

from blueapps.utils.logger import logger
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import authentication, exceptions

from settings import ENVIRONMENT


class ApiAuthentication(authentication.BaseAuthentication):
    """
    后台操作验证
    """

    def authenticate(self, request):
        try:
            req_data = json.loads(request.body)
        except Exception as e:
            logger.error(f"authenticate error:{e}")
            req_data = {}

        username = req_data.get("username", "")
        token = req_data.get("token", "")

        if not username:
            return None

        if not token:
            return None

        if ENVIRONMENT != "dev" and os.environ.get("BKAPP_LOG_API_TOKEN") != token:
            return None

        try:
            user_mode = get_user_model()
            user = user_mode.objects.get(username=username)
        except ObjectDoesNotExist:
            raise exceptions.AuthenticationFailed("No such user")

        return user, None
