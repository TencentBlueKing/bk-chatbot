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

from blueapps.account.decorators import login_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from common.http.request import init_views
from src.manager.module_intent.models import Intent, Task, Utterances


@login_exempt
@csrf_exempt
def admin_describe_intents(request):
    """
    获取意图列表
    """
    req_data, ret_data = init_views(request)
    if not self_check_permission(request):
        return JsonResponse({"result": False, "message": "bk_app_code or bk_app_secret is wrong"})
    data = req_data.get("data", {})
    data["is_deleted"] = False
    deep_filter = {k: data.pop(k) for k, v in data.copy().items() if isinstance(v, list) and not k.endswith("__in")}
    intents = Intent.query_intent_list(**data)

    if deep_filter:
        ret_data["data"] = [
            intent
            for intent in intents
            if all("all" in intent[k] or set(intent[k]) >= set(v) for k, v in deep_filter.items())
        ]
    else:
        ret_data["data"] = intents

    return JsonResponse(ret_data)


@login_exempt
@csrf_exempt
def admin_describe_tasks(request):
    """
    获取任务
    """
    req_data, ret_data = init_views(request)
    if not self_check_permission(request):
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
    if not self_check_permission(request):
        return JsonResponse({"result": False, "message": "bk_app_code or bk_app_secret is wrong"})
    data = req_data.get("data", {})
    ret_data["data"] = Utterances.query_utterances(**data)
    return JsonResponse(ret_data)


def self_check_permission(data):
    return data.GET.get("bk_app_code", True) and data.GET.get("bk_app_secret", True)
