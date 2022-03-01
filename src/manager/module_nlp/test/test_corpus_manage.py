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

from module_nlp.models import Corpus


@pytest.mark.django_db
class TestCorpusManage:
    def test_create(self, client, fake_corpus):
        """
        添加数据
        @return:
        """
        assert Corpus.objects.count() == 0
        rsp = client.post(
            "/api/v1/corpus/manage/",
            data=fake_corpus,
            content_type="application/json",
        )

        rsp_json = rsp.json()
        assert rsp_json.get("result")
        assert Corpus.objects.count() == 1

    def test_bulk_create(self, client, fake_bulk_corpus):
        """
        批量添加
        @return:
        """

        assert Corpus.objects.count() == 0
        rsp = client.post(
            path="/api/v1/corpus/manage/bulk_create/",
            data=fake_bulk_corpus,
            content_type="application/json",
        )
        rsp_json = rsp.json()
        assert rsp_json.get("result")
        assert Corpus.objects.count() == len(fake_bulk_corpus.get("data"))

    def test_list(self, client, fake_corpus_obj):
        """
        展示
        @return:
        """
        assert Corpus.objects.count() == 1
        rsp = client.get("/api/v1/corpus/manage/")
        rsp_json = rsp.json()
        assert rsp_json.get("count") == 1

    def test_gw_list(self, admin_client, fake_corpus_obj):
        """
        展示
        @return:
        """
        assert Corpus.objects.count() == 1
        rsp = admin_client.get("/api/v1/corpus/manage/gw_list/")
        rsp_json = rsp.json()
        assert rsp_json.get("count") == 1

    def test_update(self, client, faker, fake_corpus_obj):
        """
        更新数据
        @return:
        """
        assert Corpus.objects.count() == 1

        text = faker.word()
        data = {
            "text": faker.word(),
            "slots": [
                {
                    "key": faker.word(),
                    "value": faker.word(),
                    "index": [
                        faker.random.randint(0, len(text)),
                        faker.random.randint(0, len(text)),
                    ],
                }
            ],
        }
        rsp = client.put(
            f"/api/v1/corpus/manage/{fake_corpus_obj.id}/",
            data=data,
            content_type="application/json",
        )
        rsp_json = rsp.json()
        assert rsp_json.get("result")

    def test_del(self, client, fake_corpus_obj):
        """
        删除数据
        @return:
        """
        assert Corpus.objects.count() == 1
        rsp = client.delete(f"/api/v1/corpus/manage/{fake_corpus_obj.id}/")
        assert rsp.json().get("result")
        assert Corpus.objects.count() == 0
