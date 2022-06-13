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
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.response import Response

from common.drf.validation import validation
from common.drf.view_set import (
    BaseCreateViewSet,
    BaseDelViewSet,
    BaseGetViewSet,
    BaseUpdateViewSet,
)
from common.perm.permission import check_permission
from src.manager.module_nlp.models import Corpus, CorpusDomain, CorpusIntent
from src.manager.module_nlp.proto import (
    CorpusDomainSerializer,
    CorpusIntentSerializer,
    CorpusSerializer,
    ReqPostBlukCorpus,
    ReqPostCorpus,
    ReqPostCorpusIntent,
    corpus_bulk_create_docs,
    corpus_create_docs,
    corpus_delete_docs,
    corpus_domain_create_docs,
    corpus_domain_delete_docs,
    corpus_domain_list_docs,
    corpus_domain_update_docs,
    corpus_gw_list_docs,
    corpus_intent_create_docs,
    corpus_intent_delete_docs,
    corpus_intent_list_docs,
    corpus_list_docs,
    corpus_put_docs,
)


@method_decorator(name="list", decorator=corpus_domain_list_docs)
@method_decorator(name="create", decorator=corpus_domain_create_docs)
@method_decorator(name="update", decorator=corpus_domain_update_docs)
@method_decorator(name="destroy", decorator=corpus_domain_delete_docs)
class DomainViewSet(BaseGetViewSet, BaseCreateViewSet, BaseUpdateViewSet, BaseDelViewSet):
    """
    领域管理
    """

    queryset = CorpusDomain.objects.all()
    serializer_class = CorpusDomainSerializer
    filterset_class = CorpusDomain.OpenApiFilter


@method_decorator(name="list", decorator=corpus_intent_list_docs)
@method_decorator(name="create", decorator=corpus_intent_create_docs)
@method_decorator(name="destroy", decorator=corpus_intent_delete_docs)
class IntentViewSet(BaseGetViewSet, BaseCreateViewSet, BaseDelViewSet):
    """
    意图管理
    """

    queryset = CorpusIntent.objects.all()
    serializer_class = CorpusIntentSerializer
    filterset_class = CorpusIntent.OpenApiFilter

    @check_permission("gw_create")
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @validation(ReqPostCorpusIntent)
    def create(self, request, *args, **kwargs):
        """
        数据添加
        """
        payload = request.payload
        corpus_intent_object = CorpusIntent.create_intent(**payload)
        return Response(
            {
                "id": corpus_intent_object.id,
                "domain_id": corpus_intent_object.domain_id,
                "intent_key": corpus_intent_object.intent_key,
                "intent_name": corpus_intent_object.intent_name,
                "slots": corpus_intent_object.slots,
            }
        )

    @validation(ReqPostCorpusIntent)
    @action(detail=False, methods=["POST"])
    def gw_create(self, request, *args, **kwargs):
        """
        数据添加
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        payload = request.payload
        corpus_intent_object = CorpusIntent.create_intent(**payload)
        return Response(
            {
                "id": corpus_intent_object.id,
                "domain_id": corpus_intent_object.domain_id,
                "intent_key": corpus_intent_object.intent_key,
                "intent_name": corpus_intent_object.intent_name,
                "slots": corpus_intent_object.slots,
            }
        )


@method_decorator(name="list", decorator=corpus_list_docs)
@method_decorator(name="gw_list", decorator=corpus_gw_list_docs)
@method_decorator(name="create", decorator=corpus_create_docs)
@method_decorator(name="bulk_create", decorator=corpus_bulk_create_docs)
@method_decorator(name="update", decorator=corpus_put_docs)
@method_decorator(name="destroy", decorator=corpus_delete_docs)
class CorpusViewSet(BaseUpdateViewSet, BaseDelViewSet):
    """
    语料管理
    """

    queryset = Corpus.objects.all()
    serializer_class = CorpusSerializer

    @check_permission("gw_list")
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        数据查询
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        payload = request.payload
        corpus_list = Corpus.query_corpus(**payload)
        return Response(corpus_list)

    @validation(ReqPostCorpus)
    def create(self, request, *args, **kwargs):
        """
        数据添加
        """
        payload = request.payload
        Corpus.create_corpus(**payload)
        return Response({})

    @action(detail=False, methods=["POST"])
    @validation(ReqPostBlukCorpus)
    def bulk_create(self, request, *args, **kwargs):
        """
        批量添加数据
        """
        payload = request.payload
        corpus_list = payload.get("data", [])
        for corpus in corpus_list:
            Corpus.create_corpus(**corpus)
        return Response({})

    @action(detail=False, methods=["GET"])
    def gw_list(self, request, *args, **kwargs):
        """
        数据查询
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        payload = request.payload
        corpus_list = Corpus.query_corpus(**payload)
        return Response(corpus_list)
