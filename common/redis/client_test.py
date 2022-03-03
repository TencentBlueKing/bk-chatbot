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

from fakeredis import FakeServer, FakeStrictRedis


class FakeRedis(FakeStrictRedis):
    def __init__(self, **kwargs):
        server = FakeServer()
        super().__init__(server)

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        return True

    def get(self, key):
        return super(FakeRedis, self).get(key)

    def hash_set(self, name, key, val):
        return super().hset(name, key, val)

    def hash_get(self, name, key):
        return super(FakeRedis, self).hget(name, key)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        return
