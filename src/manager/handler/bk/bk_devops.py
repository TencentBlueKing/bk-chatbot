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

from common.constants import DEVOPS_HOST
from src.manager.handler.api.devops import DevOps


class BkDevOps:
    def __init__(self, username, project_id, pipeline_id, build_id):
        """
        @param username:    用户
        @param project_id:  项目id
        @param pipeline_id: 流水线id
        @param build_id:    构建id
        """
        self.username = username
        self.project_id = project_id
        self.pipeline_id = pipeline_id
        self.build_id = build_id

    def _get_fail_stage(self):
        ret = DevOps.app_build_status(
            bk_username=self.username,
            project_id=self.project_id,
            pipeline_id=self.pipeline_id,
            build_id=self.build_id,
        )
        data = ret.get("data", {})

        # 失败的stage
        stage_arr = data.get("stageStatus")
        fail_stage_arr = list(
            filter(
                lambda stage: stage.get("status") == "FAILED",
                stage_arr,
            )
        )

        if len(fail_stage_arr) != 1:
            raise ValueError("失败stage数量不为1")

        # 失败的task_id
        error_task_ids = list(
            map(
                lambda error_info: error_info.get("taskId"),
                data.get("errorInfoList", []),
            )
        )
        return {"fail_stage": fail_stage_arr[0], "error_task_ids": error_task_ids}

    def _operate_pipeline(self, task_id, failed_container, skip):
        """
        操作流水线
        @param task_id:
        @param failed_container:
        @param skip:
        @return:
        """
        ret = DevOps.app_build_retry(
            bk_username=self.username,
            project_id=self.project_id,
            pipeline_id=self.pipeline_id,
            build_id=self.build_id,
            task_id=task_id,
            failed_container=failed_container,
            skip=skip,
        )
        return ret

    @property
    def pipeline_url(self):
        uri = f"{DEVOPS_HOST}/console/pipeline/{self.project_id}/{self.pipeline_id}/detail/{self.build_id}"
        return uri

    def get_params(self):
        """
        获取提交参数
        @return:
        """
        build_status = self.get_build_status()
        data_dict = build_status.get("data", "")
        params = data_dict.get("buildParameters", [])  # 流水线参数
        param_list = list(
            map(
                lambda x: {
                    "name": x.get("key"),
                    "value": x.get("value"),
                },
                params,
            )
        )
        return param_list

    def get_build_status(self):
        """
        获取流水线信息
        @return:
        """
        return DevOps.app_build_status(
            bk_username=self.username,
            project_id=self.project_id,
            pipeline_id=self.pipeline_id,
            build_id=self.build_id,
        )

    def operate_pipeline(self, task_id, skip):
        """
        操作流水线
        @param task_id:
        @return:
        """

        # 如果存在task_id则操作task_id不存在则操作对应的stage
        fail_stage_dict = self._get_fail_stage()
        fail_stage = fail_stage_dict.get("fail_stage")
        fail_stage_id = fail_stage.get("stageId")
        error_task_ids = fail_stage_dict.get("error_task_ids")
        if not task_id or task_id not in error_task_ids:
            task_id = fail_stage_id
        return self._operate_pipeline(task_id, True, skip)

    def stop_pipeline(self):
        """
        停止流水线
        @return:
        """
        ret = DevOps.app_build_stop(
            bk_username=self.username,
            project_id=self.project_id,
            pipeline_id=self.pipeline_id,
            build_id=self.build_id,
        )
        return ret

    def retry(self, task_id):
        """
        重试
        @param task_id:
        @return:
        """
        return self.operate_pipeline(task_id, False)

    def skip(self, task_id):
        """
        跳过
        @param task_id:
        @return:
        """
        return self.operate_pipeline(task_id, True)
