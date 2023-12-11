#!/usr/bin/env python
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

from adapter.api import DevOpsApi
from common.constants import TaskExecStatus

dev_ops_instance_status_map = {
    "QUEUE": TaskExecStatus.INIT.value,  # 未执行
    "QUEUE_CACHE": TaskExecStatus.INIT.value,  # 未执行
    "RUNNING": TaskExecStatus.RUNNING.value,  # 执行中
    "FAILED": TaskExecStatus.FAIL.value,  # 失败
    "STAGE_SUCCESS": TaskExecStatus.SUCCESS.value,  # 已完成
    "SUCCEED": TaskExecStatus.SUCCESS.value,  # 已完成
    "SUSPENDED": TaskExecStatus.SUSPENDED.value,  # 暂停
    "CANCELED": TaskExecStatus.REMOVE.value,  # 已终止
    "TERMINATE": TaskExecStatus.REMOVE.value,  # 已终止
    "QUEUE_TIMEOUT": TaskExecStatus.REMOVE.value,  # 已终止
    "SKIP": TaskExecStatus.INIT.value,  # 未执行,
    "REVIEWING": TaskExecStatus.RUNNING.value,
    "REVIEW_ABORT": TaskExecStatus.FAIL.value,
    "REVIEW_PROCESSED": TaskExecStatus.SUCCESS.value,
    "PREPARE_ENV": TaskExecStatus.RUNNING.value,
    "UNEXEC": TaskExecStatus.INIT.value,
    "QUALITY_CHECK_FAIL": TaskExecStatus.FAIL.value,
    "LOOP_WAITING": TaskExecStatus.RUNNING.value,
    "TRY_FINALLY": TaskExecStatus.RUNNING.value,
    "EXEC_TIMEOUT": TaskExecStatus.FAIL.value,
    "RETRY": TaskExecStatus.RUNNING.value,
    "PAUSE": TaskExecStatus.SUSPENDED.value,
    "DEPENDENT_WAITING": TaskExecStatus.RUNNING.value,
    "QUALITY_CHECK_PASS": TaskExecStatus.SUCCESS.value,
    "QUALITY_CHECK_WAIT": TaskExecStatus.RUNNING.value,
    "TRIGGER_REVIEWING": TaskExecStatus.RUNNING.value,
    "UNKNOWN": TaskExecStatus.INIT.value,
}


class DevOps:
    @classmethod
    def app_project_list(cls, bk_username: str) -> dict:
        """
        获取项目的流水线列表
        """

        params = {"bk_username": bk_username, "page": 1, "pageSize": 500}
        ret = DevOpsApi.app_project_list(params=params, raw=True)
        return ret

    @classmethod
    def app_pipeline_list(cls, bk_username: str, project_id: str) -> dict:
        """
        获取项目的流水线列表
        """

        params = {"bk_username": bk_username, "projectId": project_id, "page": 1, "pageSize": 1000}

        ret = DevOpsApi.app_pipeline_list(params=params, raw=True)
        return ret

    @classmethod
    def app_pipeline_get(cls, bk_username: str, project_id: str, pipeline_id: str) -> dict:
        params = {"bk_username": bk_username, "projectId": project_id, "pipelineId": pipeline_id}

        ret = DevOpsApi.app_pipeline_get(params=params, raw=True)
        return ret

    @classmethod
    def app_build_start_info(cls, bk_username: str, project_id: str, pipeline_id: str) -> dict:
        """
        获取流水线启动参数
        """
        params = {
            "bk_username": bk_username,
            "projectId": project_id,
            "pipelineId": pipeline_id,
        }

        ret = DevOpsApi.app_build_start_info(params=params, raw=True)
        return ret

    @classmethod
    def app_build_status(cls, bk_username: str, project_id: str, pipeline_id: str, build_id: str):
        """
        流水线启动参数
        """
        params = {
            "bk_username": bk_username,
            "projectId": project_id,
            "pipelineId": pipeline_id,
            "buildId": build_id,
        }
        ret = DevOpsApi.app_build_status(params=params, raw=True)
        ret_data = ret.get("data", {})
        status = ret_data.get("status", "")
        return {
            "ok": ret != "",
            "status": dev_ops_instance_status_map.get(status, "1"),
            "data": ret_data,
        }

    @classmethod
    def app_build_detail(cls, bk_username: str, project_id: str, pipeline_id: str, build_id: str):
        """
        流水线启动参数
        """
        params = {
            "bk_username": bk_username,
            "projectId": project_id,
            "pipelineId": pipeline_id,
            "buildId": build_id,
        }
        rsp = DevOpsApi.app_build_detail(params=params, raw=True)
        return rsp

    @classmethod
    def app_build_start(cls):
        """
        开始构建
        """
        pass

    @classmethod
    def app_build_stop(cls, bk_username: str, project_id: str, pipeline_id: str, build_id: str):
        """
        停止构建
        """
        params = {
            "bk_username": bk_username,
            "projectId": project_id,
            "pipelineId": pipeline_id,
            "buildId": build_id,
        }
        rsp = DevOpsApi.app_build_stop(params=params, raw=True)
        return rsp

    @classmethod
    def app_build_retry(
        cls,
        bk_username: str,
        project_id: str,
        pipeline_id: str,
        build_id: str,
        task_id: str,
        failed_container=False,
        skip=False,
    ):
        """
        重试流水线
        """
        params = {
            "bk_username": bk_username,
            "projectId": project_id,
            "pipelineId": pipeline_id,
            "buildId": build_id,
            "taskId": task_id,
            "failedContainer": failed_container,
            "skip": skip,
        }
        rsp = DevOpsApi.app_build_retry(params=params, raw=True)
        return rsp
