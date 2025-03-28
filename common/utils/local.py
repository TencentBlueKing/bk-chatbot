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

import uuid
from _thread import get_ident

from werkzeug.local import Local as _Local
from werkzeug.local import release_local

wz_local = _Local()


def new_request_id():
    return uuid.uuid4().hex


class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
            return cls._instance
        self = object.__new__(cls, *args, **kwargs)
        object.__setattr__(self, "__storage__", {})
        object.__setattr__(self, "__ident_func__", get_ident)
        return self


class Local(Singleton):
    """
    local对象
    必须配合中间件RequestProvider使用
    """

    @property
    def request(self):
        """获取全局request对象"""
        request = getattr(wz_local, "request", None)
        return request

    @request.setter
    def request(self, value):
        """
        设置全局request对象
        """
        wz_local.__setattr__("request", value)

    @property
    def request_id(self):
        if self.request:
            return self.request.request_id

        return new_request_id()

    @property
    def request_username(self):
        if self.request:
            return self.request.user.username
        return "System"

    def get_http_request_id(self):
        """
        生成一个新的request_id
        """
        return new_request_id()

    @staticmethod
    def release():
        release_local(wz_local)


local = Local()
