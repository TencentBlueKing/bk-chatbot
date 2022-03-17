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


from unittest.mock import patch

import pytest


@pytest.fixture()
def fake_devops_project_id(faker) -> str:
    """
    项目ID
    """
    return str(faker.unique.random_int())


@pytest.fixture()
def fake_devops_projects(faker, fake_devops_project_id) -> dict:
    """
    项目列表
    """
    return_data = {
        "code": 0,
        "data": list(
            map(
                lambda x: {
                    "bk_biz_id": fake_devops_project_id,
                    "name": faker.first_name(),
                    "project_id": faker.first_name(),
                },
                range(0, faker.unique.random_int(5, 10)),
            )
        ),
        "result": True,
        "message": faker.name(),
        "request_id": faker.uuid4(),
    }
    return return_data


@pytest.fixture()
def fake_devops_pipelines(faker, fake_devops_project_id) -> dict:
    """
    流水线列表
    """
    return_data = {
        "code": 0,
        "data": list(
            map(
                lambda x: {
                    "bk_biz_id": fake_devops_project_id,
                    "name": faker.first_name(),
                    "id": faker.first_name(),
                },
                range(0, faker.unique.random_int(5, 10)),
            )
        ),
        "result": True,
        "message": faker.name(),
        "request_id": faker.uuid4(),
    }
    return return_data


@pytest.fixture()
def fake_devops_pipelines_start_info(faker) -> dict:
    """
    执行参数
    """
    return_data = {
        "result": True,
        "code": 200,
        "message": "OK",
        "data": list(
            map(
                lambda x: {
                    "id": faker.text(max_nb_chars=5),
                    "required": True,
                    "type": "STRING",
                    "defaultValue": "",
                    "desc": faker.text(max_nb_chars=100),
                    "label": faker.text(max_nb_chars=5),
                    "placeholder": faker.text(max_nb_chars=5),
                    "propertyType": "BUILD",
                },
                range(0, faker.unique.random_int(5, 10)),
            )
        ),
        "request_id": "e38012fb-091c-4f9f-87f5-d2461243b09b",
    }

    return return_data


@pytest.mark.view
@pytest.mark.django_db
class TestTaskViewSet:
    @patch("handler.api.devops.DevOps.app_project_list")
    def test_describe_devops_projects(self, app_project_list, fake_biz_id, client, fake_devops_projects):
        """
        项目数量
        """

        app_project_list.return_value = fake_devops_projects
        uri = f"/api/v1/task/{fake_biz_id}/describe_devops_projects/"
        response = client.get(uri)
        assert len(response.json().get("data")) == len(fake_devops_projects.get("data"))
        assert app_project_list.called

    @patch("handler.api.devops.DevOps.app_pipeline_list")
    def test_describe_devops_pipelines(self, app_pipeline_list, client, fake_devops_project_id, fake_devops_pipelines):
        """
        流水线数量
        """

        app_pipeline_list.return_value = fake_devops_pipelines
        uri = f"/api/v1/task/{fake_devops_project_id}/describe_devops_pipelines/"
        response = client.get(uri)
        assert len(response.json().get("data")) == len(fake_devops_pipelines.get("data"))
        assert app_pipeline_list.called

    @patch("handler.api.devops.DevOps.app_build_start_info")
    def test_describe_devops_pipelines_params(
        self, app_build_start_info, faker, client, fake_devops_project_id, fake_devops_pipelines_start_info
    ):
        """
        参数
        """

        app_build_start_info.return_value = fake_devops_pipelines_start_info
        data = {"pipeline_id": faker.text(max_nb_chars=10)}
        uri = f"/api/v1/task/{fake_devops_project_id}/describe_devops_pipelines_params/"
        response = client.get(uri, data=data)
        assert len(response.json().get("data")) == len(fake_devops_pipelines_start_info.get("data"))
        assert app_build_start_info.called
