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
from concurrent.futures import ThreadPoolExecutor

from celery.task import periodic_task

from src.manager.module_intent.constants import (
    UPDATE_TASK_MAX_WORKERS,
    UPDATE_TASK_PREFIX,
    UPDATE_TASK_TIME,
)
from common.redis import RedisClient
from src.manager.module_intent.handler.task_log import update_task_status


@periodic_task(run_every=datetime.timedelta(seconds=UPDATE_TASK_TIME))
def task_status_timer():
    """
    更新日志定时任务
    """
    with RedisClient() as r:
        ids = r.keys(f"{UPDATE_TASK_PREFIX}*")

    # 多线程更新状态
    with ThreadPoolExecutor(max_workers=UPDATE_TASK_MAX_WORKERS) as pool:
        list(
            map(
                lambda x: pool.submit(
                    update_task_status,
                    int(
                        x.replace(
                            f"{UPDATE_TASK_PREFIX}",
                            "",
                        )
                    ),
                ),  # (网络IO)多线程获取状态
                ids,
            )
        )
