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
import uuid
from concurrent.futures import ThreadPoolExecutor

from blueapps.utils.logger import logger_celery as logger
from celery.task import periodic_task
from common.redis import RedisClient
from src.manager.module_intent.constants import UPDATE_TASK_MAX_WORKERS, UPDATE_TASK_PREFIX
from src.manager.module_intent.handler.task_log import update_task_status


@periodic_task(run_every=datetime.timedelta(seconds=30), soft_time_limit=300)
def task_status_timer():
    """
    更新日志定时任务
    """
    _task_id = str(uuid.uuid4())
    logger.info(f"[{_task_id}]task_status_timer start task")
    try:
        with RedisClient() as r:
            get_lock_ok = r.set_nx("task_status_timer", 1, 300)
            if not get_lock_ok:
                logger.info(f"[{_task_id}]task_status_timer get lock fail,skip")
                return
            ids = r.keys(f"{UPDATE_TASK_PREFIX}*")
        logger.info(f"[{_task_id}]task_status_timer get lock and get cache with success, ids: {ids}")
        # 多线程更新状态
        with ThreadPoolExecutor(max_workers=UPDATE_TASK_MAX_WORKERS) as pool:
            list(map(lambda x: pool.submit(update_task_status, int(x.replace(f"{UPDATE_TASK_PREFIX}", ""))), ids))

        with RedisClient() as r:
            r.expire("task_status_timer", 0)
        logger.info(f"[{_task_id}]task_status_timer start finish")
    except Exception:
        with RedisClient() as r:
            r.expire("task_status_timer", 0)
        logger.exception(f"[{_task_id}]task_status_timer error")
