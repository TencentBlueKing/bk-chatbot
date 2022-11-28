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

from django.http import JsonResponse
from django.shortcuts import render

BKAPP_SUPERUSER = [i for i in os.getenv("BKAPP_SUPERUSER", "").split(",") if i]

BKAPP_FRONTEND_SHOW_HEADERS = [i for i in os.getenv("BKAPP_FRONTEND_SHOW_HEADERS", "").split(",") if i]
BKAPP_FRONTEND_SHOW_NAVS = [i for i in os.getenv("BKAPP_FRONTEND_SHOW_NAVS", "").split(",") if i]
BKAPP_SOPS_HOST = os.getenv("BKAPP_SOPS_HOST", "")
BKAPP_JOB_HOST = os.getenv("BKAPP_JOB_HOST", "")


def home(request):
    """
    首页
    """
    return render(request, "index.html")


def config(request):
    """
    前端配置信息
    """
    config_info = {
        "showHeaderList": BKAPP_FRONTEND_SHOW_HEADERS,
        "showNavList": BKAPP_FRONTEND_SHOW_NAVS,
        "env": {"BKAPP_SOPS_HOST": BKAPP_SOPS_HOST, "BKAPP_JOB_HOST": BKAPP_JOB_HOST},
    }
    return JsonResponse({"code": 0, "result": True, "data": config_info})
