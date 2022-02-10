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
from typing import Optional, Any, ClassVar

from redis import Redis
from elasticsearch import Elasticsearch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from component.config import (
    REDIS_DB_NAME, REDIS_DB_PASSWORD, REDIS_DB_PORT,
    ES_DB_DOMAIN, ES_DB_PORT, ES_DB_USERNAME, ES_DB_PASSWORD,
    ORM_URL
)


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
            self.redis_client = Redis(
                host=self.host, port=self.port, db=self.db_name, decode_responses=True
            )
        else:
            self.host = REDIS_DB_NAME
            self.password = REDIS_DB_PASSWORD
            self.port = REDIS_DB_PORT
            self.redis_client = Redis(
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

    def hash_del(self, name, key):
        return self.redis_client.hdel(name, key)

    def pipe_set(self, data):
        with self.redis_client.pipeline(transaction=False) as pipe:
            for k, v in data.items():
                pipe.set(k, json.dumps(v))
            pipe.execute()


class ESClient:
    def __init__(self):
        self.es = Elasticsearch([{'host': ES_DB_DOMAIN, 'port': ES_DB_PORT}],
                                http_auth=(ES_DB_USERNAME, ES_DB_PASSWORD), timeout=600)

    def search(self, **kwargs):
        return self.es.search(**kwargs)


class OrmClient:
    """
    this support most of object relation db,
    user need to set its db engine
    """
    def __init__(self, url: str = ORM_URL):
        engine = create_engine(url)
        db_session = sessionmaker(bind=engine)
        self.session = db_session()

    @property
    def session(self):
        return self.session

    def commit_handle(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.session.commit()
            return result
        return wrapper

    def query(self, cls: ClassVar, func: str, **params) -> Any:
        return getattr(self.session.query(cls).filter_by(**params), func)()

    @commit_handle
    def add(self, obj: Optional):
        if isinstance(obj, list):
            self.session.add_all(obj)
        else:
            self.session.add(obj)

    @commit_handle
    def delete(self, obj: Optional):
        self.session.delete(obj)

    @commit_handle
    def update(self, obj: Optional, **params):
        obj.update(params)

    def __del__(self):
        self.session.close()
