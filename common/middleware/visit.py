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
import traceback

from blueapps.utils.logger import logger

from common.constants import USER_VISIT
from common.http.request import get_request_biz_id, get_request_user
from common.redis import RedisClient

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x


class VisitMiddleware(MiddlewareMixin):
    """
    通用中间件
    """

    def process_request(self, request):
        """
        入中间件用来处理请求数据
        """
        user_name = get_request_user(request)
        biz_id = get_request_biz_id(request)
        # biz_id为数字:该功能异常不会影响正常的业务逻辑
        try:
            if not biz_id or not user_name:
                return
            biz_id = int(biz_id)
            key = f"{USER_VISIT}_{user_name}"
            with RedisClient() as r:
                r.set(key, biz_id, 60 * 60 * 24 * 7)
        except Exception:  # pylint: disable=broad-except
            logger.error(json.dumps({"message": traceback.format_exc()}))
            return
