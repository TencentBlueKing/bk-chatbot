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

from adapter.api import CCApi
from blueapps.utils.logger import logger


class CC:
    """
    cc接口
    """
    def search_business(self, bk_username, condition, fields=None):
        """
        业务信息查询
        cc.search_business({"bk_biz_id": 820})
        :param bk_username:用户名
        :param condition: 查询条件
        :param fields: 展示字段
        :return:
        """
        data = []
        kwargs = {
            "bk_username": bk_username,
            "condition": condition,
            "fields": fields,
        }
        try:
            data = CCApi.search_business(kwargs)["info"]
        except Exception as e:
            logger.error(f"[API]search_business error {e}")
        return data
