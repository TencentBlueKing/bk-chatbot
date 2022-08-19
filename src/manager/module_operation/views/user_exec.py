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
from django.db.models import Count

from common.drf.view_set import BaseViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from common.http.request import get_request_user, get_request_biz_id
from src.manager.handler.api.bk_cc import CC
from src.manager.module_intent.models import ExecutionLog


class UserExecViewSet(BaseViewSet):
    schema = None

    @action(detail=False, methods=["GET"])
    def exec_info(self, request, *args, **kwargs):
        username = get_request_user(request)
        biz_id = get_request_biz_id(request)
        data = CC().search_business(
            bk_username=username,
            biz_ids=[int(biz_id)],
            fields=["bk_biz_developer", "bk_biz_maintainer", "bk_biz_productor", "bk_biz_tester"],
        )
        variables_map = {
            "default": "default",
            "bk_biz_developer": "开发人员",
            "bk_biz_maintainer": "运维人员",
            "bk_biz_productor": "产品人员",
            "bk_biz_tester": "测试人员",
        }
        user_info = {variables_map[k]: v.split(",") if v else [] for k, v in data[0].items()}

        queryset = ExecutionLog.objects.filter(biz_id=biz_id).values("sender").annotate(exec_num=Count("id"))

        result = {"开发人员": 0, "运维人员": 0, "产品人员": 0, "测试人员": 0}
        for item in queryset:
            for user_tag, user_list in user_info.items():
                if item["sender"] in user_list:
                    result[user_tag] += item["exec_num"]
        result = [{"item": k, "value": v} for k, v in result.items()]
        return Response({"data": result})
