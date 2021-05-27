# -*- coding: utf-8 -*-

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

"""
API 统一调用模块，使用方式，举例
>>> from adapter.api import CCApi
>>> CCApi.search_business({})
"""
from django.apps import AppConfig
from django.utils.functional import SimpleLazyObject
from django.utils.module_loading import import_string


def new_api_module(module_name, api_name, module_dir="modules"):
    mod = "adapter.api.{modules}.{mod}.{api}".format(modules=module_dir, mod=module_name, api=api_name)
    return import_string(mod)()


# 对请求模块设置懒加载机制，避免项目启动出现循环引用，或者 model 提前加载

# 蓝鲸平台模块域名
BKLoginApi = SimpleLazyObject(lambda: new_api_module("bk_login", "_BKLoginApi"))
BKPAASApi = SimpleLazyObject(lambda: new_api_module("bk_paas", "_BKPAASApi"))
CCApi = SimpleLazyObject(lambda: new_api_module("cc", "_CCApi"))
GseApi = SimpleLazyObject(lambda: new_api_module("gse", "_GseApi"))
JobApi = SimpleLazyObject(lambda: new_api_module("job", "_JobApi"))
JobV3Api = SimpleLazyObject(lambda: new_api_module("jobv3", "_JobV3Api"))
CmsiApi = SimpleLazyObject(lambda: new_api_module("cmsi", "_CmsiApi"))
EsbApi = SimpleLazyObject(lambda: new_api_module("esb", "_ESBApi"))
SopsApi = SimpleLazyObject(lambda: new_api_module("sops", "_SopsApi"))

__all__ = [
    "BKLoginApi",
    "BKPAASApi",
    "CCApi",
    "JobApi",
    "JobV3Api",
    "GseApi",
    "SopsApi",
]


class ApiConfig(AppConfig):
    name = "adapter.api"
    verbose_name = "ESB_API"

    def ready(self):
        pass


default_app_config = "adapter.api.ApiConfig"
