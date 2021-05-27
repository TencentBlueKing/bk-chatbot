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

import json
from django.conf import settings
from django.http import HttpResponse
from django.template.context import Context
from adapter.common.log import logger


def render_json(dictionary={}):
    """
    return the json string for response
    @summary: dictionary也可以是string, list数据
    @note:  返回结果是个dict, 请注意默认数据格式:
                                    {'result': '',
                                     'message':''
                                    }
    """
    if type(dictionary) is not dict:
        # 如果参数不是dict,则组合成dict
        dictionary = {
            "result": True,
            "message": dictionary,
        }
    return HttpResponse(json.dumps(dictionary), content_type="application/json")


def get_context_processors_content(request):
    """
    return the context_processors dict context
    """
    context = Context()
    try:
        from django.utils.module_loading import import_string
        from django.template.context import _builtin_context_processors

        context_processors = _builtin_context_processors
        for i in settings.TEMPLATES:
            context_processors += tuple(i.get("OPTIONS", {}).get("context_processors", []))
        cp_func_list = tuple(import_string(path) for path in context_processors)
        for processors in cp_func_list:
            context.update(processors(request))
    except Exception as e:
        logger.exception("Mako: get_context_processors_content error info:%s" % e)
        context = Context()
    return context


def render_data(data, result=True, code=0, message=""):
    res = {"data": data, "result": result, "code": code, "message": message}
    return HttpResponse(json.dumps(res), content_type="application/json")
