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
from bson.objectid import ObjectId
from django.http import JsonResponse
from rest_framework.decorators import action

from common.generic import APIModelViewSet
from common.generic import ValidationMixin
from common.pagination import ResultsSetPagination
from module_api.iaas.http import init_views
from module_api.iaas.mongo_client import MongoDB
from module_api.iaas.stdlb import now
from module_faq.control.permission import FaqPermission
from module_faq.control.throttle import FaqThrottle
from module_faq.models import FAQ
from module_faq.serializers import FAQSerializer


class FaqViewSet(APIModelViewSet, ValidationMixin):
    """
    知识库操作
    """

    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    filter_fields = {
        "biz_id": ["exact"],
        "biz_name": ["exact"],
        "faq_name": ["exact"],
        "faq_db": ["exact"],
        "num": ["exact"],
        "member": ["contains", "exact", "in"],
        "created_by": ["exact"],
        "is_deleted": ["exact"],
    }
    ordering_fields = ["biz_id", "faq_name", "created_by", "updated_at"]
    ordering = "-updated_at"
    permission_classes = (FaqPermission,)
    throttle_classes = (FaqThrottle,)
    pagination_class = ResultsSetPagination

    @action(detail=False, methods=["POST"])
    def describe_qas(self, request):
        """
        查询QA
        """
        req_data, ret_data = init_views(request)
        faq_db = req_data.get("faq_db", "")
        faq_collection = req_data.get("faq_collection", "")
        if faq_db and faq_collection:
            db = MongoDB(faq_db)
            data = db.search_all({}, faq_collection)
            ret_data["data"] = list(
                map(
                    lambda x: {
                        "_id": str(x["_id"]),
                        "question": x["question"],
                        "solution": x["solution"],
                        "username": x["username"],
                    },
                    data,
                ),
            )
            db.close()

        return JsonResponse(ret_data)

    @action(detail=False, methods=["POST"])
    def create_qa(self, request):
        """
        创建QA
        """
        req_data, ret_data = init_views(request)
        questions = req_data.get("questions", [])
        solution = req_data.get("solution", "")
        username = req_data.get("username", "")
        faq_db = req_data.get("faq_db", "")
        faq_collection = req_data.get("faq_collection", "")
        now_time = now()
        data = list(
            map(
                lambda x: {
                    "question": x["value"],
                    "username": username,
                    "solution": solution,
                    "type": "",
                    "update_time": now_time,
                },
                questions,
            ),
        )

        if faq_db and faq_collection:
            db = MongoDB(faq_db)
            db.insert(data, faq_collection)
            db.close()

        return JsonResponse(ret_data)

    @action(detail=False, methods=["POST"])
    def update_qa(self, request):
        """
        变更QA
        """
        req_data, ret_data = init_views(request)
        faq_db = req_data.get("faq_db", "")
        faq_collection = req_data.get("faq_collection", "")
        questions = req_data.get("questions", [])
        solution = req_data.get("solution", "")
        username = req_data.get("username", "")
        pk = req_data.get("id", "")

        if faq_db and faq_collection:
            db = MongoDB(faq_db)
            db.update(
                {"_id": ObjectId(pk)},
                faq_collection,
                solution=solution,
                username=username,
                question=questions[0]["value"],
            )
            db.close()

        return JsonResponse(ret_data)

    @action(detail=False, methods=["POST"])
    def delete_qa(self, request):
        """
        删除QA
        """
        req_data, ret_data = init_views(request)
        faq_db = req_data.get("faq_db", "")
        faq_collection = req_data.get("faq_collection", "")
        ids = req_data.get("ids", "")
        ids = list(map(lambda x: ObjectId(x), ids))

        if faq_db and faq_collection:
            db = MongoDB(faq_db)
            db.delete({"_id": {"$in": ids}}, faq_collection)
            db.close()

        return JsonResponse(ret_data)
