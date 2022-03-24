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


from pytest import fixture

from src.manager.module_nlp.models import Corpus, CorpusDomain, CorpusIntent


@fixture()
def fake_corpus_domain(faker) -> dict:
    """
    模拟语料领域
    @param faker:
    @return:
    """
    return {"domain_key": faker.word(), "domain_name": faker.word()}


@fixture()
def fake_corpus_domain_obj(fake_corpus_domain) -> CorpusDomain:
    """
    模拟添加一条模拟语料领域数据
    @param fake_corpus_domain:
    @return:
    """
    corpus_domain_obj = CorpusDomain.objects.create(**fake_corpus_domain)
    return corpus_domain_obj


@fixture()
def fake_corpus_intent(faker, fake_corpus_domain_obj):
    """
    模拟语料意图
    @return:
    """
    return {
        "domain_id": fake_corpus_domain_obj.id,
        "intent_key": faker.word(),
        "intent_name": faker.word(),
        "slots": [{"key": faker.word(), "value": faker.word()}],
    }


@fixture()
def fake_corpus_intent_obj(fake_corpus_intent):
    """
    @param fake_corpus_intent:
    @return:
    """
    corpus_intent_obj = CorpusIntent.objects.create(**fake_corpus_intent)
    return corpus_intent_obj


@fixture()
def fake_corpus(faker, fake_corpus_intent_obj):
    """
    @param fake_corpus_intent_obj:
    @return:
    """
    return {
        "intent_id": fake_corpus_intent_obj.id,
        "data_source": faker.word(),
        "corpus_list": [
            {
                "text": faker.text(),
                "slots": [
                    {
                        "key": faker.word(),
                        "value": faker.word(),
                        "index": [faker.random_int(), faker.random_int()],
                    },
                ],
            },
        ],
    }


@fixture()
def fake_bulk_corpus(faker, fake_corpus):
    """
    @param faker:
    @param fake_corpus:
    @return:
    """
    return {"data": [fake_corpus for _ in range(faker.random.randint(1, 10))]}


@fixture()
def fake_corpus_obj(fake_corpus_intent_obj, fake_corpus):
    """
    @return:
    """

    corpus_list = fake_corpus.get("corpus_list")
    data = {
        "domain_id": fake_corpus_intent_obj.id,
        "intent_id": fake_corpus.get("intent_id"),
        "data_source": fake_corpus.get("data_source"),
        "text": corpus_list[0].get("text"),
        "slots": corpus_list[0].get("slots"),
    }
    corpus_log = Corpus.objects.create(**data)
    return corpus_log
