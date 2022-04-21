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

from django.conf import settings

API_ROOTS = [
    # 蓝鲸平台模块域名
    "BK_LOGIN_APIGATEWAY_ROOT",
    "BK_PAAS_APIGATEWAY_ROOT",
    "BK_AUTH_APIGATEWAY_ROOT",
    "CC_APIGATEWAY_ROOT",
    "CC_APIGATEWAY_ROOT_V2",
    "GSE_APIGATEWAY_ROOT",
    "TOF_APIGATEWAY_ROOT",
    "TOF3_APIGATEWAY_ROOT",
    "GSE_APIGATEWAY_ROOT_V2",
    "ESB_APIGATEWAY_ROOT_V2",
    "MONITOR_APIGATEWAY_ROOT",
    "USER_MANAGE_APIGATEWAY_ROOT",
    # 数据平台模块域名
    "ACCESS_APIGATEWAY_ROOT",
    "AUTH_APIGATEWAY_ROOT",
    "DATAQUERY_APIGATEWAY_ROOT",
    "DATABUS_APIGATEWAY_ROOT",
    "STOREKIT_APIGATEWAY_ROOT",
    "META_APIGATEWAY_ROOT",
    # 信息推送
    "CMSI_API_ROOT",
    "WECHAT_APIGATEWAY_ROOT",
    # 节点管理
    "BK_NODE_APIGATEWAY_ROOT",
    # LOG_SEARCH
    "LOG_SEARCH_APIGATEWAY_ROOT",
    "SOPS_APIGATEWAY_ROOT_V2",
    "SOPS_APIGW",
    "BK_ITSM_APIGW",
]

domain_module = "adapter.sites.{}.config.domains".format(settings.RUN_VER)
module = __import__(domain_module, globals(), locals(), ["*"])

for _root in API_ROOTS:
    try:
        locals()[_root] = getattr(module, _root)
    except Exception:  # pylint: disable=broad-except
        pass

__all__ = API_ROOTS
