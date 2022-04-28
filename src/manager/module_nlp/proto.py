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
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.serializers import Serializer

from common.drf.serializers import (
    BaseModelSerializer,
    BaseRspSerializer,
    BaseSerializer,
)
from src.manager.module_nlp.models import Corpus, CorpusDomain, CorpusIntent


class CorpusDomainSerializer(serializers.ModelSerializer):
    """
    语料领域验证器
    """

    domain_key = serializers.CharField(label="领域key")
    domain_name = serializers.CharField(label="领域名称")

    class Meta:
        model = CorpusDomain
        fields = ["id", "domain_key", "domain_name", "created_at"]


class RspGetCorpusDomain(BaseRspSerializer):
    """
    语料领域: get响应
    """

    class RspGetCorpusDomainData(Serializer):
        id = serializers.IntegerField(label="表ID")
        domain_key = serializers.IntegerField(label="领域key")
        domain_name = serializers.CharField(label="领域名称")
        created_at = serializers.CharField(label="添加时间")

    count = serializers.IntegerField(label="数量")
    data = serializers.ListField(child=RspGetCorpusDomainData())


class RspPostPutCorpusDomain(BaseRspSerializer):
    """
    语料领域: post/put响应
    """

    class RspPostPutCorpusDomainData(Serializer):
        id = serializers.IntegerField(label="表ID")
        domain_key = serializers.IntegerField(label="领域key")
        domain_name = serializers.CharField(label="领域名称")
        created_at = serializers.CharField(label="添加时间")

    data = RspPostPutCorpusDomainData()


class CorpusIntentSerializer(BaseModelSerializer):
    """
    语料意图验证器
    """

    domain_id = serializers.IntegerField(required=False, label="领域名称")
    intent_key = serializers.CharField(required=False, label="意图key")
    intent_name = serializers.CharField(required=False, label="意图name")
    slots = serializers.ListField(required=False, label="词槽")

    class Meta:
        model = CorpusIntent
        fields = ["id", "domain_id", "intent_key", "intent_name", "slots", "created_at"]


class RspGetCorpusIntent(BaseRspSerializer):
    """
    语料意图: get响应
    """

    class RspGetCorpusIntentData(Serializer):
        class RspGetCorpusIntentDataSlots(Serializer):
            key = serializers.CharField(label="词槽key")
            value = serializers.CharField(label="词槽value")

        id = serializers.IntegerField(label="表ID")
        domain_id = serializers.IntegerField(label="领域名称")
        intent_key = serializers.CharField(label="意图key")
        intent_name = serializers.CharField(label="意图name")
        slots = serializers.ListField(label="词槽", child=RspGetCorpusIntentDataSlots())
        created_at = serializers.CharField(label="添加时间")

    count = serializers.IntegerField(label="数量")
    data = serializers.ListField(child=RspGetCorpusIntentData())


class ReqPostCorpusIntent(Serializer):
    """
    添加语料意图
    """

    class ReqPostCorpusIntentSlots(Serializer):
        key = serializers.CharField(label="词槽key")
        value = serializers.CharField(label="词槽value")

    domain_id = serializers.IntegerField(label="领域名称")
    intent_key = serializers.CharField(label="意图key")
    intent_name = serializers.CharField(label="意图name")
    slots = serializers.ListField(label="词槽", child=ReqPostCorpusIntentSlots())


class RspPostCorpusIntent(BaseRspSerializer):
    """
    添加语料意图响应
    """

    class RspPostCorpusIntentData(ReqPostCorpusIntent):
        id = serializers.IntegerField(label="唯一id")

    data = RspPostCorpusIntentData()


class ReqGetCorpus(BaseSerializer):
    """
    查询语料
    """

    domain_id_list = serializers.ListField(required=False, label="领域id")
    intent_id = serializers.IntegerField(required=False, label="意图id")
    intent_name = serializers.CharField(required=False, label="意图名称")
    created_by = serializers.CharField(required=False, label="添加人")
    updated_by = serializers.CharField(required=False, label="修改人")
    text = serializers.CharField(required=False, label="语句")
    data_source = serializers.CharField(required=False, label="数据来源")
    order_by = serializers.CharField(required=False, label="排序")


class RspGetCorpus(BaseRspSerializer):
    """
    查询语料响应
    """

    class RspPostCorpusData(Serializer):
        class RspPostCorpusDataDomain(Serializer):
            id = serializers.IntegerField(label="领域唯一id")
            name = serializers.CharField(label="领域名称")

        class RspPostCorpusDataIntent(Serializer):
            id = serializers.IntegerField(label="意图唯一id")
            name = serializers.CharField(label="意图名称")
            slots = serializers.DictField(label="词槽map")

        class RspPostCorpusDataSlots(Serializer):
            key = serializers.CharField(label="词槽key")
            value = serializers.CharField(label="词槽value")
            index = serializers.ListField(child=serializers.IntegerField(), label="词槽索引")

        id = serializers.IntegerField(label="语料唯一id")
        domain = RspPostCorpusDataDomain()
        intent = RspPostCorpusDataIntent()
        data_source = serializers.CharField(label="语料来源")
        text = serializers.CharField(label="语料文本信息")
        slots = serializers.ListField(child=RspPostCorpusDataSlots())
        created_at = serializers.CharField(label="添加时间")
        created_by = serializers.CharField(label="添加人")
        updated_at = serializers.CharField(label="修改时间")
        updated_by = serializers.CharField(label="修改人")

    count = serializers.IntegerField(label="数量")
    data = serializers.ListField(child=RspPostCorpusData())


class ReqPostCorpus(Serializer):
    """
    添加语料
    """

    class ReqGetCorpusList(Serializer):
        class ReqGetCorpusListSlots(Serializer):
            key = serializers.CharField(required=False, label="文本数据")
            value = serializers.CharField(required=False, label="词槽的值")
            index = serializers.ListField(child=serializers.IntegerField(), min_length=2, max_length=2, label="索引")

        text = serializers.CharField(required=False, label="文本数据")
        slots = serializers.ListField(child=ReqGetCorpusListSlots(), label="词槽信息")

    intent_id = serializers.IntegerField(required=False, label="意图id")
    data_source = serializers.CharField(required=False, label="数据来源")
    corpus_list = serializers.ListField(child=ReqGetCorpusList(), label="数据来源")


class ReqPostBlukCorpus(Serializer):
    """
    批量添加语料
    """

    data = serializers.ListField(child=ReqPostCorpus())


class RspPutCorpus(BaseRspSerializer):
    """
    修改语料响应
    """

    class RspPutCorpusData(Serializer):
        class RspPutCorpusSlots(Serializer):
            key = serializers.CharField(label="词槽key")
            value = serializers.CharField(label="词槽value")
            index = serializers.ListField(child=serializers.IntegerField(), label="词槽索引")

        id = serializers.IntegerField(label="语料唯一id")
        text = serializers.CharField(label="语料文本信息")
        slots = serializers.ListField(child=RspPutCorpusSlots())

    data = RspPutCorpusData()


class CorpusSerializer(BaseModelSerializer):
    """
    语料验证
    """

    text = serializers.CharField(required=False, label="文本")
    slots = serializers.ListField(
        child=ReqPostCorpus.ReqGetCorpusList.ReqGetCorpusListSlots(),
        required=False,
        label="词槽",
    )

    class Meta:
        model = Corpus
        fields = ["id", "text", "slots"]


############################################################

corpus_tag = ["语料"]

corpus_domain_list_docs = swagger_auto_schema(
    tags=corpus_tag,
    responses={200: RspGetCorpusDomain()},
    operation_id="语料领域管理-查看",
)
corpus_domain_create_docs = swagger_auto_schema(
    tags=corpus_tag,
    request_body=CorpusDomainSerializer,
    responses={200: RspPostPutCorpusDomain()},
    operation_id="语料领域管理-添加领域",
)
corpus_domain_update_docs = swagger_auto_schema(
    tags=corpus_tag,
    responses={200: RspPostPutCorpusDomain()},
    operation_id="语料领域管理-修改",
)
corpus_domain_delete_docs = swagger_auto_schema(
    tags=corpus_tag,
    responses={200: BaseRspSerializer()},
    operation_id="语料领域管理-删除语料",
)
############################################################
corpus_intent_list_docs = swagger_auto_schema(
    tags=corpus_tag,
    operation_id="语料意图管理-查看",
    responses={200: RspGetCorpusIntent()},
)
corpus_intent_create_docs = swagger_auto_schema(
    tags=corpus_tag,
    request_body=ReqPostCorpusIntent,
    operation_id="语料意图管理-添加意图",
    responses={200: RspPostCorpusIntent()},
)
corpus_intent_delete_docs = swagger_auto_schema(
    tags=corpus_tag,
    operation_id="语料意图管理-删除语料",
    responses={200: BaseRspSerializer()},
)
############################################################
corpus_list_docs = swagger_auto_schema(
    tags=corpus_tag,
    operation_id="语料管理-展示",
    query_serializer=ReqGetCorpus(),
    responses={200: RspGetCorpus()},
)
corpus_create_docs = swagger_auto_schema(
    tags=corpus_tag,
    request_body=ReqPostCorpus,
    responses={200: BaseRspSerializer()},
    operation_id="语料管理-添加",
)
corpus_bulk_create_docs = swagger_auto_schema(
    tags=corpus_tag,
    request_body=ReqPostBlukCorpus,
    responses={200: BaseRspSerializer()},
    operation_id="语料管理-批量添加",
)
corpus_put_docs = swagger_auto_schema(
    tags=corpus_tag,
    responses={200: RspPutCorpus()},
    operation_id="语料管理-修改",
)
corpus_delete_docs = swagger_auto_schema(
    tags=corpus_tag,
    responses={200: BaseRspSerializer()},
    operation_id="语料管理-删除",
)

############################################################
corpus_gw_list_docs = swagger_auto_schema(
    tags=corpus_tag,
    operation_id="语料管理APIGW-展示",
    query_serializer=ReqGetCorpus(),
    responses={200: RspGetCorpus()},
)
