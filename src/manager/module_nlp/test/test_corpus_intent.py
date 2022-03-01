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


import pytest

from module_nlp.models import CorpusIntent


@pytest.mark.django_db
class TestCorpusIntent:
    def test_create(self, client, fake_corpus_intent):
        """
        添加语料意图
        @param client:
        @param fake_corpus_intent:
        @return:
        """
        assert CorpusIntent.objects.count() == 0
        rsp = client.post(
            "/api/v1/corpus/intent/",
            data=fake_corpus_intent,
            content_type="application/json",
        )
        rsp_json = rsp.json()
        assert rsp_json.get("code") == 200
        assert CorpusIntent.objects.count() == 1

    def test_list(self, client, fake_corpus_intent_obj):
        """
        展示语料意图
        @return:
        """
        assert CorpusIntent.objects.count() == 1
        rsp = client.get("/api/v1/corpus/intent/")
        rsp_json = rsp.json()
        assert rsp_json.get("code") == 200
        assert rsp_json.get("count") == 1

    def test_del(self, client, fake_corpus_intent_obj):
        """
        删除语料意图
        @param client:
        @param fake_corpus_intent_obj:
        @return:
        """
        assert CorpusIntent.objects.count() == 1
        rsp = client.delete(f"/api/v1/corpus/intent/{fake_corpus_intent_obj.id}/")
        rsp_json = rsp.json()
        assert rsp_json.get("code") == 200
        assert CorpusIntent.objects.count() == 0
