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
import os

import redis
from blueapps.utils.logger import logger


class RedisClient:
    """
    redis操作
    """

    def __init__(self, host=None, password=None, port=None, db="0"):
        """
        初始化
        """
        self.host = host if host else os.environ.get("BKAPP_REDIS_DB_NAME", "localhost")
        self.password = password if password else os.environ.get("BKAPP_REDIS_DB_PASSWORD", "")
        self.port = port if port else int(os.environ.get("BKAPP_REDIS_DB_PORT", "6379"))
        self.redis_client = redis.Redis(
            host=self.host,
            password=self.password,
            port=self.port,
            db=db,
            decode_responses=True,
        )

    def get(self, key):
        data = self.redis_client.get(key)
        try:
            data = json.loads(data)
        except Exception as e:
            logger.error(f"REDIS GET ERR [{str(e)}]")
        return data

    def hash_set(self, name, key, val):
        self.redis_client.hset(name, key, val)

    def set_nx(self, key, value, timeout):
        """
        设置唯一锁的时候设置过期时间
        """
        ok = self.redis_client.setnx(key, value)
        if ok or self.redis_client.ttl(key) == 0:
            self.redis_client.expire(key, timeout)
        return ok

    def hash_get(self, name, key):
        return self.redis_client.hget(name, key)

    def pipe_set(self, **kwargs):
        with self.redis_client.pipeline(transaction=False) as pipe:
            for k, v in kwargs.items():
                pipe.set(k, json.dumps(v))
            pipe.execute()

    def __enter__(self):
        return self.redis_client

    def __exit__(self, *args, **kwargs):
        return
