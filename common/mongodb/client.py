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

from pymongo import MongoClient

from settings import ENVIRONMENT


class MongoDB:
    url = ""

    def __init__(self, db_name):
        if ENVIRONMENT == "dev":
            self._client = MongoClient(host="127.0.0.1", port=27017)
        else:
            self.host = os.environ.get("BKAPP_MONGO_DB_IP")
            self.port = os.environ.get("BKAPP_MONGO_DB_PORT")
            self.user = os.environ.get("BKAPP_MONGO_DB_NAME")
            self.password = os.environ.get("BKAPP_MONGO_DB_PASSWORD")
            self.url = "mongodb://{}:{}@{}:{}".format(
                self.user,
                self.password,
                self.host,
                self.port,
            )
            self._client = MongoClient(self.url)
            self._db = self._client[db_name]

    def insert(self, data, collection_name):
        collection = self._db[collection_name]
        result = collection.insert_many(data)
        return result.inserted_ids

    def search(self, condition, collection_name):
        collection = self._db[collection_name]
        cursor = collection.find_one(condition)
        return cursor

    def search_all(self, condition, collection_name):
        collection = self._db[collection_name]
        cursor = collection.find(condition)
        return cursor

    def delete(self, condition, collection_name):
        collection = self._db[collection_name]
        result = collection.delete_many(condition)
        return result.deleted_count

    def update(self, condition, collection_name, **kwargs):
        collection = self._db[collection_name]
        obj = collection.find_one(condition)
        if obj:
            obj.update(kwargs)
            result = collection.update(condition, obj)
            return result
        else:
            condition.update(kwargs)
            return self.insert([condition], collection_name)

    def close(self):
        self._client.close()
