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
import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from blueapps.account.decorators import login_exempt

from module_api.iaas.http import init_views
from module_intent.models import Intent
from module_intent.models import Task
from module_intent.models import Utterances


@login_exempt
@csrf_exempt
def admin_describe_intents(request):
    """
    获取意图列表
    """
    req_data, ret_data = init_views(request)
    if not self_check_permission(req_data):
        return JsonResponse({"result": False, "message": "bk_app_code or bk_app_secret is wrong"})
    data = req_data.get("data", {})
    data["is_deleted"] = False
    available_user = data.pop("available_user") if data.__contains__("available_user") else []
    intents = Intent.query_intent_list(**data)
    if available_user:
        ret_data['data'] = [intent for intent in intents
                            if set(intent['available_user'])
                            >= set(available_user)
                            ]
        return JsonResponse(ret_data)
    else:
        ret_data['data'] = intents
        return JsonResponse(ret_data)


@login_exempt
@csrf_exempt
def admin_describe_tasks(request):
    """
    获取任务
    """
    req_data, ret_data = init_views(request)
    if not self_check_permission(req_data):
        return JsonResponse({"result": False, "message": "bk_app_code or bk_app_secret is wrong"})
    data = req_data.get("data", {})
    ret_data["data"] = Task.query_task_list(**data)
    return JsonResponse(ret_data)


@login_exempt
@csrf_exempt
def admin_describe_utterances(request):
    """
    获取语料
    """
    req_data, ret_data = init_views(request)
    if not self_check_permission(req_data):
        return JsonResponse({"result": False, "message": "bk_app_code or bk_app_secret is wrong"})
    data = req_data.get("data", {})
    ret_data["data"] = Utterances.query_utterances(**data)
    return JsonResponse(ret_data)


def self_check_permission(data):
    if data.get("bk_app_code", "") == settings.APP_ID and data.get("bk_app_secret", "") == settings.APP_TOKEN:
        return True
    return False
