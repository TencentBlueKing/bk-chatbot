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

import requests

from common.constants import PLUGIN_RELOAD_URI


class Service:
    def __init__(self):
        self._host = os.getenv("PLUGIN_URI")
        self._headers = self._generate_headers()

    def _generate_headers(self):
        return {
            "Content-Type": "application/json",
            "User-Name": os.getenv("PLUGIN_USER_NAME"),
            "Api-Token": os.getenv("PLUGIN_API_TOKEN"),
        }

    def _call(self, action: str, method: str, **params):
        """
        @param action: 调用路由
        @param method: 调用方法
        @param params: 调用参数
        @return:
        """
        url = f"{self._host}{action}"
        params["headers"] = self._headers
        rsp = getattr(requests, method)(url, **params)
        try:
            ret_json = rsp.json()
            return ret_json
        except TypeError:
            return {}

    def call_service(self, **params):
        """
        调用插件服务
        @param params: 调用参数
        @return:
        """
        ret_json = self._call("/api/rest/v1/service/call", "post", json=params)
        code = ret_json.get("code", 1)
        if code != 0:
            return {"message": ret_json.get("message")}
        return ret_json.get("data")


class PluginManage(Service):
    def __init__(self, env):
        super().__init__()
        self._host = os.getenv(env)

    def add_service(self, **params):
        """
        添加插件服务
        @param params: 调用参数
        @return:
        """

        return self._call("/api/rest/v2/service/alter/", "put", json=params)

    def del_service(self, key):
        """
        删除插件服务
        @param key: 插件key
        @return:
        """
        return self._call(f"/api/rest/v2/service/del/{key}", "delete")

    def get_exec_count(self, **params):
        """
        获取执行历史
        @param key:
        @return:
        """
        return self._call("/api/rest/v2/service/exec/num", "get", params=params)

    def reload(self, bot_name):
        """
        reload机器人配置
        @return:
        """
        params = {"bot_name": bot_name}
        rsp = requests.post(PLUGIN_RELOAD_URI, json=params)
        return rsp
