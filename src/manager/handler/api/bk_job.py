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


import os

from blueapps.utils.logger import logger

from adapter.api import JobV2Api, JobV3Api


class JobV3:
    """
    JOB3.0 接口
    """

    @classmethod
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

    @classmethod
    def get_job_instance_status(self, bk_username: str, bk_biz_id: int, job_instance_id: str, return_ip_result=False):
        """
        根据作业实例 ID 查询作业执行状态
        作业状态码:
        :param bk_username: 用户
        :param bk_biz_id:业务ID
        :param job_instance_id: int 作业执行实例ID
        :param return_ip_result: int 是否返回IP结果
        :return:
        """
        kwargs = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "job_instance_id": job_instance_id,
            "return_ip_result": return_ip_result,
        }
        response = JobV3Api.get_job_instance_status(kwargs)
        job_instance = response.get("job_instance", {})
        ok = response.get("finished", False)
        job_status = job_instance.get("status", {})
        return {
            "ok": ok,
            "status": job_status,
            "data": response,
        }

    @classmethod
    def get_job_instance_global_var_value(cls, bk_username: str, bk_biz_id: int, job_instance_id: str):
        """查询Job执行任务的详情
        :param bk_username:
        :param bk_biz_id:
        :param job_instance_id:
        :return:
        """
        kwargs = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "job_instance_id": job_instance_id,
        }

        response = JobV3Api.get_job_instance_global_var_value(kwargs)
        return response

    @classmethod
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

    @classmethod
    def get_job_instance_list(self, bk_username, bk_biz_id, **params):
        """
        查询作业实例列表（执行历史) V3
        """
        kwargs = {"bk_username": bk_username, "bk_biz_id": bk_biz_id}
        kwargs.update(params)
        response = JobV3Api.get_job_instance_list(kwargs, raw=True)
        return response

    @classmethod
    def get_job_instance_ip_log(
        cls, bk_username: str, bk_biz_id: int, job_instance_id: int, step_instance_id: int, bk_cloud_id: int, ip: str
    ):
        """
        :param bk_username:      用户名
        :param bk_biz_id:        业务id
        :param job_instance_id:  作业实例ID
        :param step_instance_id: 步骤实例ID
        :param bk_cloud_id:      云区域ID
        :param ip:               IP
        """
        kwargs = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "job_instance_id": job_instance_id,
            "step_instance_id": step_instance_id,
            "bk_cloud_id": bk_cloud_id,
            "ip": ip,
        }
        response = JobV3Api.get_job_instance_ip_log(kwargs, raw=True)
        return response

    @classmethod
    def operate_job_instance(cls, username: str, biz_id: int, job_instance_id: int, operation_code: int = 1):
        """
        作业实例操作: 只有当流程正常的时候才能进行终止
        """
        kwargs = {
            "bk_username": username,
            "bk_biz_id": biz_id,
            "job_instance_id": job_instance_id,
            "operation_code": operation_code,
        }
        rsp = JobV3Api.operate_job_instance(kwargs, raw=True)
        return rsp

    @classmethod
    def operate_step_instance(
        cls, username: str, biz_id: int, job_instance_id: int, step_instance_id: int, operation_code: int
    ):
        """
        步骤实例操作
        """
        kwargs = {
            "bk_username": username,
            "bk_biz_id": biz_id,
            "job_instance_id": job_instance_id,
            "step_instance_id": step_instance_id,
            "operation_code": operation_code,
        }
        rsp = JobV3Api.operate_step_instance(kwargs, raw=True)
        return rsp

    @classmethod
    def save_cron(
        cls,
        bk_username: str,
        bk_biz_id: int,
        job_plan_id: int,
        id: int,
        name: str,
        expression: str,
        execute_time: str,
        timer_id: int,
    ):
        """
        保存定时任务
        """
        params = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "job_plan_id": job_plan_id,
            "id": id,
            "name": name,
            "execute_time": execute_time,
            "expression": expression,
            "global_var_list": [
                {
                    "name": "timer_id",
                    "value": str(timer_id),
                    "type": 1,
                },
            ],
        }
        rsp = JobV3Api.save_cron(params, raw=True)
        return rsp

    @classmethod
    def update_cron_status(cls, bk_username: str, bk_biz_id: int, id: int, status: int):
        """
        更新定时作业状态，如启动或暂停
        """
        params = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "id": id,
            "status": status,
        }
        rsp = JobV3Api.update_cron_status(params, raw=True)
        return rsp


class JobV2:
    def __init__(self):
        return

    @classmethod
    def get_job_plan_list(self, bk_username, bk_biz_id, **params):
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
        rsp = JobV2Api.get_job_list(kwargs)
        # job_v2适配v3的数据结构
        logger.info(rsp)
        plan_list = list(
            map(
                lambda x: {
                    "bk_biz_id": x.get("bk_biz_id", ""),
                    "id": x.get("bk_job_id", ""),
                    "name": x.get("name", ""),
                    "creator": x.get("creator", ""),
                    "last_modify_time": x.get("last_modify_time", ""),
                    "create_time": x.get("create_time", ""),
                    "job_template_id": x.get("job_template_id", ""),
                    "last_modify_user": x.get("last_modify_user"),
                },
                rsp,
            )
        )
        return {"data": {"data": plan_list}}

    @classmethod
    def get_job_plan_detail(self, bk_username, bk_biz_id, job_plan_id):
        """
        根据作业执行方案ID查询作业执行方案详情 V3
        """
        kwargs = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "bk_job_id": job_plan_id,
        }
        rsp = JobV2Api.get_job_detail(kwargs, raw=True)
        logger.info(rsp)
        data = rsp.get("data", {})

        # 删除多余数据
        data.setdefault("global_var_list", data.get("global_vars", []))
        data.setdefault("step_list", data.get("steps", []))
        if hasattr(data, "global_vars"):
            del data["global_vars"]
        if hasattr(data, "steps"):
            del data["steps"]
        return rsp


JOB = JobV2 if os.getenv("BKAPP_JOB_VERSION", "V3") == "V2" else JobV3
