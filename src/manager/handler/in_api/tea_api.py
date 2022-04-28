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


from common.utils.os import get_env_or_raise

from .base import BaseApi


class TeaAPI(BaseApi):
    def __init__(self, **kwargs):
        """
        使用默认配置
        """
        host = kwargs.get("host", get_env_or_raise("TEA_URL"))
        key = kwargs.get("key", get_env_or_raise("TEA_API_KEY"))
        user = kwargs.get("user", get_env_or_raise("TEA_OPERATOR"))
        sub = kwargs.get("sub", get_env_or_raise("TEA_API_ID"))
        super().__init__(host, key, user, sub)

    def get_product(self, **params):
        """
        tea系统获取业务信息
        """
        return self._call(action="/api/v1/product", method="get", params=params)

    def get_valid_product(self, **params):
        """
        获取有效产品
        @param params:
        @return:
        """

        result = self.get_product(**params)
        data = result.get("data", [])
        # 过滤出有效项目
        valid_projects = list(
            filter(
                lambda x: x.get("cc_id")
                and x.get("status") not in get_env_or_raise("TEA_PRODUCT_EXCLUDE_STATUS").split(","),
                data,
            )
        )
        return valid_projects
