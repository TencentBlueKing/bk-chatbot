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


import json
from unittest.mock import patch

import pytest
from pytest import fixture

from module_intent.models import Intent, Task, Utterances


@fixture()
def fake_intent_all_data(faker, fake_biz_id) -> dict:
    """
    添加意图
    """
    return {
        "index_id": faker.pyint(),
        "biz_id": fake_biz_id,
        "intent_name": faker.word(),
        "status": faker.pybool(),
        "available_user": [faker.word() for _ in range(faker.random_int(min=1, max=5))],
        "available_group": [faker.word() for _ in range(faker.random_int(min=1, max=5))],
        "developer": [faker.word() for _ in range(faker.random_int(min=1, max=5))],
        "approver": [faker.word() for _ in range(faker.random_int(min=1, max=5))],
        "is_commit": faker.pybool(),
        "serial_number": faker.uuid4(),
        "content": [faker.word() for _ in range(faker.random_int(min=1, max=5))],
        "platform": faker.random_element(elements=("job", "sops", "devops")),
        "task_id": faker.word(),
        "project_id": faker.word(),
        "activities": [faker.word() for _ in range(faker.random_int(min=1, max=5))],
        "slots": [faker.word() for _ in range(faker.random_int(min=1, max=5))],
        "source": str({faker.word(): faker.word() for _ in range(faker.random_int(min=1, max=5))}),
        "script": faker.text(),
    }


@fixture()
def fake_intent_data(fake_intent_all_data) -> dict:
    key_list = [
        "index_id",
        "biz_id",
        "intent_name",
        "status",
        "available_user",
        "available_group",
        "developer",
        "is_commit",
        "serial_number",
    ]

    intent_dict = {key: fake_intent_all_data.get(key) for key in key_list}
    return intent_dict


@fixture()
def fake_intent(fake_biz_id, fake_intent_data) -> Intent:
    """
    添加一条意图记录
    """

    fake_intent = Intent.objects.create(**fake_intent_data)
    fake_intent.save()
    return fake_intent


@fixture()
def fake_utterances(faker, fake_intent, fake_intent_all_data) -> Utterances:
    """
    语料
    """
    utterances = Utterances.objects.create(
        biz_id=int(fake_intent.biz_id),
        index_id=fake_intent.id,
        content=fake_intent_all_data.get("content"),
    )
    utterances.save()
    return utterances


@fixture()
def fake_task(faker, fake_intent, fake_intent_all_data) -> Task:
    """
    任务
    """
    key_list = [
        "platform",
        "task_id",
        "project_id",
        "activities",
        "slots",
        "source",
        "script",
    ]

    task_dict = {key: fake_intent_all_data.get(key) for key in key_list}
    task_dict.update({"biz_id": int(fake_intent.biz_id), "index_id": fake_intent.id})
    task = Task.objects.create(**task_dict)
    return task


@pytest.mark.view
@pytest.mark.django_db
@patch("module_intent.control.permission.IntentPermission.has_permission", return_value=True)
class TestIntentViewSet:
    def test_create(self, has_permission, client, fake_intent_all_data):
        """
        添加意图
        """
        assert Intent.objects.count() == 0
        assert Utterances.objects.count() == 0
        assert Task.objects.count() == 0
        biz_id = fake_intent_all_data.get("biz_id")
        response = client.post(f"/api/v1/{biz_id}/intent/", data=fake_intent_all_data)
        assert response.json().get("code") == 200
        assert Intent.objects.count() == 1
        assert Utterances.objects.count() == 1
        assert Task.objects.count() == 1
        assert has_permission.called

    def test_list(self, has_permission, client, fake_intent):
        """
        意图列表
        """
        assert Intent.objects.count() == 1
        biz_id = fake_intent.biz_id
        response = client.get(f"/api/v1/{biz_id}/intent/", data={"biz_id": biz_id})
        assert response.json().get("count") == 1
        assert has_permission.called

    def test_update(self, has_permission, faker, client, fake_intent, fake_intent_all_data):
        """
        更新意图
        """
        assert Intent.objects.count() == 1
        biz_id = fake_intent.biz_id
        id = fake_intent.id
        fake_intent_all_data["biz_id"] = biz_id
        intent_name = faker.word()
        fake_intent_all_data["intent_name"] = intent_name
        response = client.put(
            f"/api/v1/{biz_id}/intent/{id}/",
            data=json.dumps(fake_intent_all_data),
            content_type="application/json",
        )
        assert response.json().get("code") == 200
        assert response.json().get("data").get("intent_name") == intent_name
        assert has_permission.called

    def test_delete(self, has_permission, client, fake_intent):
        """
        删除意图
        """

        assert Intent.objects.count() == 1
        response = client.delete(f"/api/v1/{fake_intent.biz_id}/intent/{fake_intent.id}/")
        assert response.json().get("code") == 200
        assert Intent.objects.count() == 0
        assert has_permission.called

    def test_fetch_intent_count(self, has_permission, client, fake_intent):
        """
        测试意图数量
        """
        assert Intent.objects.count() == 1
        response = client.post(f"/api/v1/{fake_intent.biz_id}/intent/fetch_intent_count/")
        assert response.json().get("data") == dict(count=1)
        assert has_permission.called
