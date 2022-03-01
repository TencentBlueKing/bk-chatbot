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

from common.constants import PlatformType, TaskExecStatus
from module_intent.handler import TaskType
from module_intent.models import ExecutionLog


@pytest.fixture()
def fake_query_biz_id(fake_biz_id) -> dict:
    """
    查询条件
    """

    return {"data": {"biz_id": fake_biz_id}}


@pytest.fixture()
def fake_execution_log_data(faker, fake_biz_id) -> dict:
    """
    添加日志的dict
    """
    return {
        "biz_id": fake_biz_id,
        "intent_id": faker.unique.random_int(),
        "intent_name": faker.first_name(),
        "intent_create_user": faker.first_name(),
        "bot_name": faker.first_name(),
        "bot_type": faker.first_name(),
        "platform": faker.unique.random_int(1, 5),
        "task_id": faker.unique.random_int(),
        "sender": faker.first_name(),
        "msg": faker.text(),
        "status": str(faker.unique.random_int(0, 5)),
        "rtx": faker.first_name(),
        "params": [{"id": faker.word(), "name": faker.word(), "value": faker.word()}],
    }


@pytest.fixture()
def fake_execution_log(fake_execution_log_data) -> ExecutionLog:
    """
    添加一条执行记录
    """
    fake_log = ExecutionLog.objects.create(**fake_execution_log_data)
    fake_log.save()
    return fake_log


@pytest.fixture()
def fake_create_log_data(login_exempt_info, fake_execution_log_data) -> dict:
    """
    添加一条执行记录
    """
    post_data = {"data": fake_execution_log_data}
    post_data.update(login_exempt_info)
    return post_data


@pytest.fixture()
def fake_get_job_instance_list(faker) -> dict:
    """
    执行历史列表
    """
    data = list(
        map(
            lambda x: {
                "job_instance_id": faker.unique.random_int(),
                "bk_biz_id": faker.unique.random_int(),
                "name": faker.word(),
                "total_time": faker.unique.random_int(),
                "type": faker.unique.random_int(),
                "start_time": faker.unix_time(),
                "create_time": faker.unix_time(),
                "status": faker.unique.random_int(),
                "job_template_id": faker.unique.random_int(),
                "launch_mode": faker.unique.random_int(),
                "operator": faker.first_name(),
                "job_plan_id": faker.unique.random_int(),
                "end_time": faker.unix_time(),
            },
            range(1, 10),
        )
    )

    return {
        "message": "",
        "code": 0,
        "data": {"start": 0, "length": len(data), "total": 63961, "data": data},
        "result": True,
        "request_id": faker.sha1(raw_output=False),
    }


@pytest.fixture()
def fake_running_task(fake_execution_log):
    """
    模拟正在执行的任务
    @return:
    """
    fake_execution_log.status = TaskExecStatus.RUNNING.value
    fake_execution_log.save()
    return fake_execution_log


@pytest.fixture()
def fake_fail_task(fake_execution_log):
    """
    模拟失败的任务
    @return:
    """
    fake_execution_log.status = TaskExecStatus.FAIL.value
    # fake_execution_log.platform = request.param
    fake_execution_log.save()
    return fake_execution_log


@pytest.mark.django_db
class TestExecutionLogViewSet:
    def test_list(self, client, fake_execution_log):
        response = client.get("/api/v1/log/")
        assert len(response.json().get("data")) == 1

    @patch("handler.api.bk_job.JOB.get_job_instance_list")
    def test_describe_records(self, get_job_instance_list, client, fake_get_job_instance_list):
        """
        测试执行记录
        """
        response = client.post("/api/v1/log/describe_records/")
        ret_json = response.json()
        assert len(ret_json.get("data")) == 0
        assert get_job_instance_list.called

        get_job_instance_list.return_value = fake_get_job_instance_list
        response = client.post("/api/v1/log/describe_records/")
        ret_json = response.json()
        assert len(ret_json.get("data")) == fake_get_job_instance_list.get("data").get("length")
        assert get_job_instance_list.called


@pytest.mark.django_db
class TestExecutionBotLogViewSet:
    def test_create_log(self, admin_client, fake_create_log_data):
        assert ExecutionLog.objects.count() == 0
        response = admin_client.post(
            "/api/v1/task/exec/create_log/",
            content_type="application/json",
            data=fake_create_log_data,
        )
        assert ExecutionLog.objects.count() == 1
        ret_json = response.json()
        assert ret_json.get("data", {}) == {"id": ExecutionLog.objects.get().pk}


@pytest.mark.django_db
class TestExecTaskView:
    def make_data(self, obj, platform, action) -> dict:
        """
        @param id:
        @param action:
        @return:
        """
        obj.platform = platform
        obj.save()
        return {
            "id": obj.id,
            "action": action,
            "data": {},
        }

    @pytest.mark.parametrize("action", [TaskType.RETRY.value, TaskType.SKIP.value])
    @patch("handler.api.bk_job.JOB.operate_step_instance")
    @patch("handler.api.bk_job.JOB.get_job_instance_status")
    def test_task_job_retry_and_skip(self, get_status, operate_step, faker, admin_client, fake_fail_task, action):
        """
        重试/跳过 job失败步骤
        """
        data = self.make_data(fake_fail_task, PlatformType.JOB.value, action)
        # 操作步骤部分返回
        operate_step.return_value = {
            "result": True,
            "data": {"step_instance_id": faker.random_int(), "job_instance_id": faker.random_int()},
        }
        # 获取任务状态部分返回
        get_status.return_value = {
            "result": True,
            "data": {
                "step_instance_list": [{"step_instance_id": faker.random_int(), "status": 4}],
            },
        }
        rsp = admin_client.post("/api/v1/task/exec/task_operate/", data=data)
        assert operate_step.called
        assert get_status.called
        rsp_json = rsp.json()
        assert rsp_json.get("result")

    @pytest.mark.parametrize("action", [TaskType.STOP.value])
    @patch("handler.api.bk_job.JOB.operate_job_instance")
    def test_task_job_stop(self, operate_job, admin_client, fake_running_task, action):
        """
        停止job任务
        """
        data = self.make_data(fake_running_task, PlatformType.JOB.value, action)
        operate_job.return_value = {"result": True, "data": {"job_instance_id": fake_running_task.task_id}}
        rsp = admin_client.post("/api/v1/task/exec/task_operate/", data=data)
        rsp_json = rsp.json()
        assert operate_job.called
        assert rsp_json.get("result")

    @pytest.mark.parametrize("action", [TaskType.RETRY.value, TaskType.SKIP.value])
    @patch("handler.api.bk_sops.SOPS.operate_node")
    @patch("handler.api.bk_sops.SOPS.get_task_status")
    def test_task_sops_retry_and_skip(self, get_status, operate_node, faker, admin_client, fake_fail_task, action):
        """
        重试/跳过 sops失败节点
        """
        data = self.make_data(fake_fail_task, PlatformType.SOPS.value, action)
        # 操作步骤部分返回
        operate_node.return_value = {"result": True, "data": "success", "code": 0}
        # 获取任务状态部分返回

        sops_node_id = faker.sha1(raw_output=False)
        get_status.return_value = {
            "result": True,
            "data": {
                "children": {
                    sops_node_id: {
                        "state": "FAILED",
                        "id": sops_node_id,
                    }
                },
                "state": "FAILED",
            },
        }
        rsp = admin_client.post("/api/v1/task/exec/task_operate/", data=data)
        assert operate_node.called
        assert get_status.called
        rsp_json = rsp.json()
        assert rsp_json.get("result")

    @pytest.mark.parametrize("action", [TaskType.STOP.value])
    @patch("handler.api.bk_sops.SOPS.operate_task")
    def test_task_sops_stop(self, operate_task, faker, admin_client, fake_running_task, action):
        """
        停止 sops流程
        """

        # 操作步骤部分返回
        operate_task.return_value = {"result": True, "data": {}}
        data = self.make_data(fake_running_task, PlatformType.SOPS.value, action)
        rsp = admin_client.post("/api/v1/task/exec/task_operate/", data=data)
        assert operate_task.called
        rsp_json = rsp.json()
        assert rsp_json.get("result")

    @pytest.mark.parametrize("action", [TaskType.RETRY.value, TaskType.SKIP.value])
    @patch("handler.api.devops.DevOps.app_build_status")
    @patch("handler.api.devops.DevOps.app_build_retry")
    def test_task_devops_retry_and_skip(
        self, app_build_retry, app_build_status, fake_fail_task, faker, admin_client, action
    ):
        """
        重试/跳过 蓝盾流程
        @return:
        """
        app_build_retry.return_value = {
            "data": {
                "id": faker.word(),
            },
            "message": faker.word(),
            "status": 0,
        }
        app_build_status.return_value = {
            "ok": True,
            "status": 3,
            "data": {
                "id": faker.sha1(raw_output=False),
                "status": "FAILED",
                "stageStatus": [
                    {"stageId": "stage-1", "name": "stage-1", "status": "SUCCEED"},
                    {"stageId": "stage-2", "name": "stage-2", "status": "FAILED"},
                    {"stageId": "stage-3", "name": "stage-3", "tag": ["Build"]},
                ],
            },
        }
        data = self.make_data(fake_fail_task, PlatformType.DEV_OPS.value, action)
        rsp = admin_client.post("/api/v1/task/exec/task_operate/", data=data)
        rsp_json = rsp.json()
        assert rsp_json.get("result")

    @pytest.mark.parametrize("action", [TaskType.STOP.value])
    @patch("handler.api.devops.DevOps.app_build_stop")
    def test_task_devops_stop(self, app_build_stop, faker, admin_client, fake_running_task, action):
        """
        停止 蓝盾流程
        @return:
        """
        app_build_stop.return_value = {"data": True, "message": faker.word(), "status": 0}

        data = self.make_data(fake_running_task, PlatformType.DEV_OPS.value, action)
        rsp = admin_client.post("/api/v1/task/exec/task_operate/", data=data)
        rsp_json = rsp.json()
        assert rsp_json.get("result")
