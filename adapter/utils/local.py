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

"""
记录线程变量
"""
import uuid
import sys
from threading import local

from blueapps.utils import get_request

_local = local()


def activate_request(request, request_id=None):
    """
    激活request线程变量
    """
    if not request_id:
        request_id = str(uuid.uuid4())
    request.request_id = request_id
    _local.request = request
    return request


def get_request_id():
    """
    获取request_id
    """
    try:
        return get_request().request_id
    except Exception:
        return str(uuid.uuid4())


def get_request_username():
    """
    获取请求的用户名
    """
    username = ""
    try:
        username = get_request().user.username
    except Exception:
        pass
    finally:
        if not username and "celery" in sys.argv:
            username = "admin"
    return username
