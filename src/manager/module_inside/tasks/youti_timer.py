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
import datetime
import json
import time

from celery.task import periodic_task

from common.redis import RedisClient
from common.utils.os import get_env_or_raise
from src.manager.handler.in_api.tea_api import TeaAPI
from src.manager.module_inside.handler.tea import get_product_users

YOUTI_USERS_FLUSH_TIME = int(get_env_or_raise("YOUTI_USERS_FLUSH_TIME", 60 * 60))


@periodic_task(run_every=datetime.timedelta(seconds=YOUTI_USERS_FLUSH_TIME))
def get_user_info():
    """
    获取用户信息并缓存
    @return:
    """
    valid_projects = TeaAPI().get_valid_product(**{})
    cc_id_arr = list(
        map(
            lambda x: x.get("cc_id"),
            valid_projects,
        )
    )
    product_users_list = []
    # 遍历产寻对应的任务信息
    for cc_id in cc_id_arr:
        user_info_list = list(
            map(
                lambda product_user: json.dumps(
                    {
                        "username": f"qq_{product_user.get('user_qq')}",
                        "code": product_user.get("qq_unionid"),
                        "display_name": product_user.get("real_name"),
                        "departments": list(map(lambda x: str(x), product_user.get("product_list"))),
                    }
                ),
                get_product_users(cc_id),
            )
        )
        product_users_list.extend(user_info_list)
        time.sleep(0.1)
    uniq_users_list = list(map(lambda x: json.loads(x), set(product_users_list)))
    with RedisClient() as r:
        r.set("YOUTI_USER_INFO", json.dumps(uniq_users_list), 60 * 60 * 3)
