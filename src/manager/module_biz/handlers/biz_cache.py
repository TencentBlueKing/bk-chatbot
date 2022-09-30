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

from common.redis import RedisClient
from src.manager.handler.api.bk_cc import CC
from src.manager.module_biz.constants import REDIS_BIZ_INFO_PREFIX


def get_biz_info(biz_id, operator="admin"):
    """
    根据业务ID获取业务相关信息
    """
    biz_info = {"bk_biz_name": "未知业务名"}
    if not biz_id or int(biz_id) == -1:
        return biz_info

    with RedisClient() as r:
        biz_key = f"{REDIS_BIZ_INFO_PREFIX}_{biz_id}"
        biz_info = r.get(biz_key)
        if not biz_info:
            info = CC().search_business(
                bk_username=operator,
                biz_ids=[int(biz_id)],
                fields=["bk_biz_id", "bk_biz_name"],
            )
            if info:
                biz_info = info[0]
                r.set(biz_key, json.dumps(info[0]), 60 * 60 * 24 * 7)
        else:
            biz_info = json.loads(biz_info)

    return biz_info
