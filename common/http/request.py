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
import uuid

from blueapps.utils.logger import logger


def init_views(request):
    """
    初始化request参数
    :param request: 用户请求
    """
    req_data = {}
    try:
        req_data = json.loads(request.body)
    except Exception:  # pylint: disable=broad-except
        logger.error(
            f"[INIT_VIEWS] req_data parse error {request.body}",
        )

    ret_data = {
        "result": True,
        "data": [],
        "message": "",
        "request_id": str(uuid.uuid4()),
    }
    return req_data, ret_data


def get_request_user(request) -> str:
    """
    获取用户名称
    @param request:
    @return:
    """
    return request.user.username or request.COOKIES.get("bk_uid")


def get_request_biz_id(request) -> str:
    """
    返回biz_id
    @param request:
    @return:
    """
    return request.COOKIES.get("biz_id")
