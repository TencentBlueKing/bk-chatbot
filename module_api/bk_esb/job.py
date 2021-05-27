# -*- coding: utf-8 -*-

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

from adapter.api import JobV3Api, JobApi


class JOB:
    """
    JOB3.0 接口
    """

    def get_job_list(self, bk_username, bk_biz_id, **params):
        """
        查询作业执行方案列表
        :param bk_username: 用户
        :param bk_biz_id: 业务ID
        :param params: 过滤条件
            creator
            name
            create_time_start
            create_time_end
            last_modify_user
            last_modify_time_start
            last_modify_time_end
            start
            length
        :return:
        [
            {
                "bk_biz_id": 1,
                "bk_job_id": 100,
                "name": "test",
                "creator": "admin",
                "last_modify_user": "admin",
                "create_time": "2018-01-23 15:05:41 +0800",
                "last_modify_time": "2018-01-23 16:04:51 +0800"
            }
        ]
        """
        kwargs = {"bk_username": bk_username, "bk_biz_id": bk_biz_id}
        kwargs.update(params)
        return JobApi.get_job_list(kwargs)

    def get_job_detail(self, bk_username, bk_biz_id, bk_job_id):
        """
        根据作业执行方案ID查询作业执行方案详情
        :param bk_username: 用户
        :param bk_biz_id:业务ID
        :param bk_job_id:作业执行方案ID
        :return:
        """
        kwargs = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "bk_job_id": bk_job_id,
        }
        response = JobApi.get_job_detail(kwargs)
        return response

    def get_job_instance_status(self, bk_username, bk_biz_id, job_instance_id):
        """
        根据作业实例 ID 查询作业执行状态
        作业状态码:
            1.未执行;
            2.正在执行;
            3.执行成功;
            4.执行失败;
            5.跳过;
            6.忽略错误;
            7.等待用户;
            8.手动结束;
            9.状态异常;
            10.步骤强制终止中;
            11.步骤强制终止成功
        :param bk_username: 用户
        :param bk_biz_id:业务ID
        :param job_instance_id: int 作业执行实例ID
        :return:
            status, start_time, end_time
        """
        kwargs = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "job_instance_id": job_instance_id,
        }
        response = JobV3Api.get_job_instance_status(kwargs)
        status = "1"
        data = response
        is_finished = data.get("is_finished", False)
        start_time = data.get("job_instance", {}).get("start_time", "")
        end_time = data.get("job_instance", {}).get("end_time", "")
        if is_finished:
            state = data["job_instance"]["status"]
            status = "2" if state == 3 else "3"

        return status, start_time, end_time

    def get_job_plan_list(self, bk_username, bk_biz_id, **params):
        """
        查询作业执行方案列表 V3
        {
          "bk_biz_id": 820,
          "name": "xxxxxx",
          "creator": "xxxx",
          "last_modify_time": 1601293575,
          "create_time": 1601283803,
          "job_template_id": 3945,
          "id": 1000896,
          "last_modify_user": "xxxx"
        }
        """
        kwargs = {"bk_username": bk_username, "bk_biz_id": bk_biz_id}
        kwargs.update(params)
        response = JobV3Api.get_job_plan_list(kwargs, raw=True)
        return response

    def get_job_plan_detail(self, bk_username, bk_biz_id, job_plan_id):
        """
        根据作业执行方案ID查询作业执行方案详情 V3
        """
        kwargs = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "job_plan_id": job_plan_id,
        }
        response = JobV3Api.get_job_plan_detail(kwargs, raw=True)
        return response

    def get_job_instance_list(self, bk_username, bk_biz_id, **params):
        """
        查询作业实例列表（执行历史) V3
        """
        kwargs = {"bk_username": bk_username, "bk_biz_id": bk_biz_id}
        kwargs.update(params)
        response = JobV3Api.get_job_instance_list(kwargs, raw=True)
        return response
