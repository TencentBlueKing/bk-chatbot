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

from django.db import models
from django_filters import filters

from common.dao.query import make_page, make_query
from common.drf.filters import BaseOpenApiFilter
from common.models.base import BaseModel
from common.models.json import DictCharField
from common.utils.local import local


class CorpusDomain(BaseModel):
    """
    领域
    """

    domain_name = models.CharField("领域名称", null=False, blank=True, unique=True, max_length=128)
    domain_key = models.CharField("领域key", null=False, blank=True, unique=True, max_length=128)

    class Meta:
        ordering = ["-id"]
        db_table = "tab_corpus_domain"

    @classmethod
    def create_domain(cls, **kwargs):
        """
        创建domain
        """
        return cls.objects.create(**kwargs)

    class OpenApiFilter(BaseOpenApiFilter):
        """
        提供给rest查询使用
        """

        domain_key = filters.CharFilter(field_name="domain_key")
        domain_name = filters.CharFilter(field_name="domain_name")


class CorpusIntent(BaseModel):
    """
    意图
    """

    domain_id = models.IntegerField("领域id", default=0)
    intent_key = models.CharField("意图key", null=False, blank=True, unique=True, max_length=128)
    intent_name = models.CharField("意图名称", null=False, blank=True, unique=True, max_length=128)
    slots = DictCharField("词槽")

    class Meta:
        db_table = "tab_corpus_intent"

    @classmethod
    def create_intent(cls, **kwargs):
        """
        创建词槽意图
        """
        domain_id = kwargs.get("domain_id")
        CorpusDomain.objects.get(pk=domain_id)
        return cls.objects.create(**kwargs)

    class OpenApiFilter(BaseOpenApiFilter):
        """
        提供给rest查询使用
        """

        domain_id = filters.NumberFilter(field_name="domain_id")
        intent_key = filters.CharFilter(field_name="intent_key")
        intent_name = filters.CharFilter(field_name="intent_name")


class Corpus(BaseModel):
    """
    语料
    """

    domain_id = models.IntegerField("领域id", default=0)
    intent_id = models.IntegerField("意图id", default=0)
    data_source = models.CharField("数据源", default="", max_length=128)
    text = models.TextField("文本数据", default="", null=True, blank=True)
    slots = DictCharField("词槽", default="")

    class Meta:
        db_table = "tab_corpus"

    @classmethod
    def query_corpus(cls, **kwargs):
        order_by = kwargs.get("order_by", "-id")
        domain_id_list = kwargs.get("domain_id_list")
        intent_id = kwargs.get("intent_id")
        created_by = kwargs.get("created_by")
        updated_by = kwargs.get("updated_by")
        text = kwargs.get("text")
        # 通过意图名称查询意图id
        intent_name = kwargs.get("intent_name", None)
        intent_ids = None
        if intent_name:
            intent_obj_arr = CorpusIntent.objects.filter(intent_key__contains=intent_name)
            intent_ids = list(map(lambda x: x.id, intent_obj_arr))
        created_at_min = kwargs.get("created_at_min")  # 最大时间
        created_at_max = kwargs.get("created_at_max")  # 最小时间
        page = int(kwargs.get("page", 0))
        pagesize = int(kwargs.get("pagesize", 0))
        config = {
            "intent_id": intent_id,
            "created_by": created_by,
            "updated_by": updated_by,
            "text__contains": text,
            "intent_id__in": intent_ids,
            "domain_id__in": domain_id_list,
            "create_time__gt": created_at_min,
            "create_time__lt": created_at_max,
        }
        query = make_query(config)
        total = cls.objects.filter(**query).count()
        start, end = make_page(page, pagesize=pagesize)
        corpus_obj_list = cls.objects.filter(**query).order_by(order_by)[start:end]
        # 查出语料中包含的领域和意图
        query_intent_id_list, query_domain_id_list = [], []
        for corpus_obj in corpus_obj_list:
            query_intent_id_list.append(corpus_obj.intent_id)
            query_domain_id_list.append(corpus_obj.domain_id)
        query_intent_obj_list = CorpusIntent.objects.filter(**{"id__in": set(query_intent_id_list)})
        query_domain_obj_list = CorpusDomain.objects.filter(**{"id__in": set(query_domain_id_list)})
        query_intent_obj_dict = {
            x.id: {
                "id": x.id,
                "name": x.intent_name,
                "slots": {slot.get("key"): slot.get("value") for slot in x.slots},
            }
            for x in query_intent_obj_list
        }
        query_domain_obj_dict = {
            x.id: {
                "id": x.id,
                "name": x.domain_name,
            }
            for x in query_domain_obj_list
        }
        # 组合语料 意图/领域
        corpus_list = list(
            map(
                lambda corpus_obj: {
                    "id": corpus_obj.id,
                    "domain": query_domain_obj_dict.get(corpus_obj.domain_id),
                    "intent": query_intent_obj_dict.get(corpus_obj.intent_id),
                    "data_source": corpus_obj.data_source,
                    "text": corpus_obj.text,
                    "slots": corpus_obj.slots,
                    "created_at": corpus_obj.created_at,
                    "created_by": corpus_obj.created_by,
                    "updated_at": corpus_obj.updated_at,
                    "updated_by": corpus_obj.updated_by,
                },
                corpus_obj_list,
            )
        )
        return {"count": total, "data": corpus_list}

    @classmethod
    def create_corpus(cls, **kwargs):
        intent_id = kwargs.get("intent_id")
        data_source = kwargs.get("data_source")
        corpus_list = kwargs.get("corpus_list")
        corpus_intent_obj = CorpusIntent.objects.get(id=intent_id)
        # 验证domain_id 和 意图id ==> 存储数据
        corpus_obj = list(
            map(
                lambda corpus: Corpus(
                    domain_id=corpus_intent_obj.domain_id,
                    intent_id=intent_id,
                    data_source=data_source,
                    text=corpus.get("text"),
                    slots=corpus.get("slots"),
                    created_by=local.request_username,
                    updated_by=local.request_username,
                ),
                corpus_list,
            )
        )
        # 批量添加数据
        return Corpus.objects.bulk_create(corpus_obj)

    class OpenApiFilter(BaseOpenApiFilter):
        """
        提供给rest查询使用
        """

        text = models.TextField("文本数据", default="", null=True, blank=True)
        slot = DictCharField("词槽", default="")
