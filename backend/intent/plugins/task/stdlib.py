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

import re
import json

import redis

from .settings import REDIS_DB_NAME, REDIS_DB_PASSWORD, REDIS_DB_PORT


def parse_entity(regular, msg):
    regex = re.compile(regular)
    m = regex.search(msg)
    return m.group()


class RedisClient:
    """
    redis操作
    """

    def __init__(self, db_name="0", env="dev"):
        self.db_name = db_name

        if env == "dev":
            self.host = "localhost"
            self.password = ""
            self.port = 6379
            self.redis_client = redis.Redis(
                host=self.host, port=self.port, db=self.db_name, decode_responses=True
            )
        else:
            self.host = REDIS_DB_NAME
            self.password = REDIS_DB_PASSWORD
            self.port = REDIS_DB_PORT
            self.redis_client = redis.Redis(
                host=self.host,
                password=self.password,
                port=self.port,
                db=self.db_name,
                decode_responses=True,
            )

    def set(self, key, data, ex=None, nx=False):
        self.redis_client.set(key, data, ex=ex, nx=nx)

    def get(self, key):
        data = self.redis_client.get(key)
        try:
            data = json.loads(data)
        except TypeError:
            data = []

        return data

    def hash_set(self, name, key, val):
        self.redis_client.hset(name, key, val)

    def hash_get(self, name, key):
        return self.redis_client.hget(name, key)

    def pipe_set(self, data):
        with self.redis_client.pipeline(transaction=False) as pipe:
            for k, v in data.items():
                pipe.set(k, json.dumps(v))
            pipe.execute()
