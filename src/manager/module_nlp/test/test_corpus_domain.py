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

from src.manager.module_nlp.models import CorpusDomain


@pytest.mark.django_db
class TestCorpusDomain:
    def test_create(self, client, fake_corpus_domain):
        """
        添加
        @param client:
        @param fake_corpus_domain:
        @return:
        """
        assert CorpusDomain.objects.count() == 0
        rsp = client.post(
            "/api/v1/corpus/domain/",
            data=fake_corpus_domain,
        )
        assert rsp.json().get("code") == 200
        assert CorpusDomain.objects.count() == 1

    def test_list(self, client, fake_corpus_domain_obj):
        """
        查看
        @param client:
        @param fake_corpus_domain_obj:
        @return:
        """
        assert CorpusDomain.objects.count() == 1
        rsp = client.get("/api/v1/corpus/domain/")
        assert rsp.json().get("count") == 1

    def test_update(self, client, faker, fake_corpus_domain_obj):
        """
        更新
        @param client:
        @param faker:
        @param fake_corpus_domain_obj:
        @return:
        """
        assert CorpusDomain.objects.count() == 1

        domain_key = faker.word()
        domain_name = faker.word()
        data = {"domain_key": domain_key, "domain_name": domain_name}
        rsp = client.put(
            f"/api/v1/corpus/domain/{fake_corpus_domain_obj.id}/",
            data=data,
            content_type="application/json",
        )
        assert rsp.json().get("data", {}).get("domain_key") == domain_key
        assert rsp.json().get("data", {}).get("domain_name") == domain_name

    def test_del(self, client, fake_corpus_domain_obj):
        """
        删除
        @param client:
        @param fake_corpus_domain_obj:
        @return:
        """
        assert CorpusDomain.objects.count() == 1
        rsp = client.delete(f"/api/v1/corpus/domain/{fake_corpus_domain_obj.id}/")
        assert rsp.json().get("result")
        assert CorpusDomain.objects.count() == 0
