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

import os

from adapter.api.base import DataAPI
from config.domains import BKDATA_APIGW

BKAPP_BKDATA_TONE = os.getenv("BKAPP_BKDATA_TONE")


def before_request(params: dict):
    """
    预处理参数
    @param params:
    @return:
    """
    params.update(
        **{
            "bkdata_authentication_method": "token",
            "bkdata_data_token": BKAPP_BKDATA_TONE,
        }
    )
    return params


class _BKBaseApi(object):
    MODULE = ("数据平台")

    @property
    def query_sync(self):
        """
        查询数据
        @return:
        """
        return DataAPI(
            method="POST",
            url=BKDATA_APIGW + "/queryengine/query_sync/",
            module=self.MODULE,
            description="数据查询",
            cache_time=60,
            before_request=before_request,
        )


BKBaseApi = _BKBaseApi()
