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
from rest_framework.response import Response

from common.http.request import get_request_biz_id
from common.control.throttle import ChatBotThrottle
from common.drf.generic import APIModelViewSet, ValidationMixin
from common.drf.pagination import ResultsSetPagination
from common.http.request import init_views
from common.mongodb.client import MongoDB
from common.utils.my_time import mk_now_time
from src.manager.module_other.models import FAQModel
from src.manager.module_other.proto.faq import FAQSerializer


class FaqViewSet(APIModelViewSet, ValidationMixin):
    """
    知识库操作
    """

    queryset = FAQModel.objects.all()
    serializer_class = FAQSerializer
    filterset_class = FAQModel.OpenApiFilter
    permission_classes = ()
    throttle_classes = (ChatBotThrottle,)
    ordering_fields = ["biz_id", "faq_name", "created_by", "updated_at"]
    ordering = "-updated_at"
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        return self.queryset.filter(is_deleted=False)

    def list(self, request, *args, **kwargs):
        biz_id = get_request_biz_id(request)
        queryset = self.filter_queryset(self.get_queryset().filter(biz_id=biz_id))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

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
        now_time = mk_now_time()
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
