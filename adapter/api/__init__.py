# -*- coding: utf-8 -*-


from django.apps import AppConfig

from .modules.bk_base import BKBaseApi
from .modules.bk_cc import CCApi
from .modules.bk_chat import BkChatApi
from .modules.bk_gse import GseApi
from .modules.bk_itsm import BkITSMApi
from .modules.bk_jobv2 import JobV2Api
from .modules.bk_jobv3 import JobV3Api
from .modules.bk_log import BkLog
from .modules.bk_login import BKLoginApi
from .modules.bk_monitor import BkMonitorApi
from .modules.bk_paas import BKPAASApi
from .modules.bk_sops import SopsApi
from .modules.cmsi import CmsiApi
from .modules.dev_ops import DevOpsApi
from .modules.esb import ESBApi

# from django.utils.functional import SimpleLazyObject
# from django.utils.module_loading import import_string


# def new_api_module(module_name, api_name, module_dir="modules"):
#     mod = "adapter.api.{modules}.{mod}.{api}".format(modules=module_dir, mod=module_name, api=api_name)
#     return import_string(mod)()


# 对请求模块设置懒加载机制，避免项目启动出现循环引用，或者 model 提前加载

# 蓝鲸平台模块域名
# BKLoginApi = SimpleLazyObject(lambda: new_api_module("bk_login", "_BKLoginApi"))
# BKPAASApi = SimpleLazyObject(lambda: new_api_module("bk_paas", "_BKPAASApi"))
# CCApi = SimpleLazyObject(lambda: new_api_module("bk_cc", "_CCApi"))
# GseApi = SimpleLazyObject(lambda: new_api_module("bk_gse", "_GseApi"))
# JobApi = SimpleLazyObject(lambda: new_api_module("bk_jobv2", "_JobApi"))
# JobV3Api = SimpleLazyObject(lambda: new_api_module("bk_jobv3", "_JobV3Api"))
# CmsiApi = SimpleLazyObject(lambda: new_api_module("cmsi", "_CmsiApi"))
# EsbApi = SimpleLazyObject(lambda: new_api_module("esb", "_ESBApi"))
# SopsApi = SimpleLazyObject(lambda: new_api_module("sops", "_SopsApi"))
# DevOpsApi = SimpleLazyObject(lambda: new_api_module("devops", "_DevOpsApi"))
# BkMonitorApi = SimpleLazyObject(lambda: new_api_module("bkmonitor", "_BkMonitorApi"))
# BkITSMApi = SimpleLazyObject(lambda: new_api_module("bk_itsm", "_BkITSMApi"))
# BkChatApi = SimpleLazyObject(lambda: new_api_module("bk_chat", "_BkChatApi"))

__all__ = [
    "BKLoginApi",
    "BKPAASApi",
    "CCApi",
    "JobV2Api",
    "JobV3Api",
    "GseApi",
    "SopsApi",
    "DevOpsApi",
    "BkMonitorApi",
    "BkITSMApi",
    "BkChatApi",
    "BKBaseApi",
]


class ApiConfig(AppConfig):
    name = "adapter.api"
    verbose_name = "ESB_API"

    def ready(self):
        pass


default_app_config = "adapter.api.ApiConfig"
