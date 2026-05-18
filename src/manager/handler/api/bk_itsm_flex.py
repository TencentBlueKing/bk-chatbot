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

import requests
from bkoauth.models import AccessToken
from django.conf import settings


class ItsmFlex:
    """
    监控接口
    """

    @classmethod
    def get_service_catalogue_flatten(cls, username, **kwargs):
        """
        获取服务目录
        """
        url = settings.ITSM_FLEX_APIGW + "/openapi/v1/service_catalogue/flatten/"

        try:
            access_token = AccessToken.objects.get(user_id=username).access_token
        except AccessToken.DoesNotExist:
            raise Exception(f"获取用户{username}的access_token失败")

        headers = {
            "Content-Type": "application/json",
            "X-Bkapi-Authorization": json.dumps(
                {
                    "bk_app_code": settings.APP_CODE,
                    "bk_app_secret": settings.SECRET_KEY,
                    "access_token": access_token,
                }
            ),
        }
        response = requests.get(url, headers=headers)
        result = response.json()
        return result
