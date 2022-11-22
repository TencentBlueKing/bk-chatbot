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
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response

from common.drf.view_set import BaseManageViewSet, BaseViewSet
from common.http.request import get_request_biz_id
from common.perm.permission import login_exempt_with_perm
from src.manager.module_intent.control.permission import IntentPermission
from src.manager.module_intent.models import IntentTag, Intent
from src.manager.module_intent.proto.intent_tag import IntentTagSerializer


class IntentTagViewSet(BaseManageViewSet):
    """
    技能标签管理
    """

    queryset = IntentTag.objects.all()
    serializer_class = IntentTagSerializer
    ordering = "tag_index"
    permission_classes = (IntentPermission,)

    def list(self, request, *args, **kwargs):
        biz_id = get_request_biz_id(request)
        qs = self.queryset.filter(biz_id=biz_id)
        serializer = self.get_serializer(qs, many=True)
        intent_qs = (
            Intent.objects.filter(biz_id=biz_id, is_deleted=False).values("tag_name").annotate(quote_num=Count("id"))
        )
        tag_quote_map = {item["tag_name"]: item["quote_num"] for item in intent_qs}
        data = []
        for item in serializer.data:
            data.append({"quote_num": tag_quote_map.get(item["tag_name"], 0), **item})
        return Response({"data": data})

    @action(detail=False, methods=["POST"])
    def batch_save(self, request, *args, **kwargs):
        biz_id = get_request_biz_id(request)
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        new_tag_name_set = {d["tag_name"] for d in serializer.data}
        if len(new_tag_name_set) != len(serializer.data):
            return Response({"message": "同一业务下标签名不能相同"}, exception=True)

        db_qs = self.queryset.filter(biz_id=biz_id)
        old_tag_name_set = {q.tag_name for q in db_qs}

        delete_tag_name_set = old_tag_name_set - new_tag_name_set

        intent_qs = (
            Intent.objects.filter(biz_id=biz_id, is_deleted=False).values("tag_name").annotate(quote_num=Count("id"))
        )
        tag_name_quote_set = {item["tag_name"] for item in intent_qs if item["quote_num"]}

        delete_quoted_tag_name = tag_name_quote_set & delete_tag_name_set

        if delete_quoted_tag_name:
            return Response({"message": f"标签{delete_quoted_tag_name}正在被引用，不能删除"}, exception=True)

        new_tag_obj_list = []
        for index, tag_data in enumerate(serializer.data):
            new_tag_obj_list.append(
                IntentTag(**{"biz_id": biz_id, "tag_name": tag_data["tag_name"], "tag_index": index})
            )
        with transaction.atomic():
            db_qs.delete()
            IntentTag.objects.bulk_create(new_tag_obj_list)

        return Response()


class IntentTagGwViewSet(BaseViewSet):
    """
    技能标签管理
    """

    queryset = IntentTag.objects.all()
    ordering = "tag_index"

    @login_exempt_with_perm
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        biz_id = request.query_params.get("biz_id", "")
        qs = self.queryset.filter(biz_id=biz_id)
        serializer = IntentTagSerializer(qs, many=True)
        intent_qs = (
            Intent.objects.filter(biz_id=biz_id, is_deleted=False).values("tag_name").annotate(quote_num=Count("id"))
        )
        tag_quote_map = {item["tag_name"]: item["quote_num"] for item in intent_qs}
        data = []
        for item in serializer.data:
            data.append({"quote_num": tag_quote_map.get(item["tag_name"], 0), **item})
        return Response({"data": data})
