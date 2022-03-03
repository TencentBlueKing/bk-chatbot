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

import operator
from functools import reduce

from common.constants import JOB_HOST
from src.manager.handler.api.bk_job import JOB


class BkJob:
    def __init__(self, biz_id, username, task_id):
        """
        @param biz_id:  业务Id
        @param username:具有权限的人
        @param task_id: 任务(实例)id
        """
        self.biz_id = biz_id
        self.username = username
        self.instance_id = task_id

    def __get_fail_step_id(self) -> int:
        """
        获取失败步骤ID
        @return:
        """
        ret = JOB.get_job_instance_status(
            bk_username=self.username,
            bk_biz_id=self.biz_id,
            job_instance_id=self.instance_id,
        )

        # 获取失败步骤的step_id
        step_instance_list = ret.get("data", {}).get("step_instance_list", [])
        # 执行失败的步骤
        fail_step = list(filter(lambda x: x.get("status") == 4, step_instance_list))
        if len(fail_step) == 0:
            raise ValueError("不存在失败的步骤")
        return fail_step[0].get("step_instance_id")

    def operate_fail_step(self, action: int):
        """
        操作失败节点
        @return:
        """
        step_id = self.__get_fail_step_id()
        ret = JOB.operate_step_instance(
            username=self.username,
            biz_id=self.biz_id,
            job_instance_id=self.instance_id,
            step_instance_id=step_id,
            operation_code=action,
        )
        return ret

    def get_job_instance_status(self, return_ip_result=False):
        """
        获取Job的状态
        @param return_ip_result:
        @return:
        """
        return JOB.get_job_instance_status(
            bk_username=self.username,
            bk_biz_id=self.biz_id,
            job_instance_id=self.instance_id,
            return_ip_result=return_ip_result,
        )

    def get_var_value(self):
        """
        获取job参数
        @return:
        """
        return JOB.get_job_instance_global_var_value(
            bk_username=self.username,
            bk_biz_id=self.biz_id,
            job_instance_id=self.instance_id,
        )

    def get_uniq_var_value(self):
        """
        全局参数去重
        @return:
        """
        params_value = self.get_var_value()
        # 获取作业实例全局变量值
        step_instance_var_list = params_value.get("step_instance_var_list")
        # 全局变量参数
        global_var_list = list(map(lambda x: x.get("global_var_list"), step_instance_var_list))
        param_list = []
        if global_var_list:
            param_list = reduce(operator.add, global_var_list)
        # 参数去重
        return [dict(param) for param in {tuple(param_dict.items()) for param_dict in param_list}]

    @property
    def url(self):
        """
        返回job链接
        @return:
        """
        return f"{JOB_HOST}/{self.biz_id}/execute/task/{self.instance_id}"

    def terminate(self):
        """
        终止
        @return:
        """

        ret = JOB.operate_job_instance(
            username=self.username,
            biz_id=self.biz_id,
            job_instance_id=self.instance_id,
        )
        return ret

    def retry_fail(self):
        """
        失败IP重做
        @return:
        """
        return self.operate_fail_step(2)

    def ignore_error(self):
        """
        忽略错误
        @return:
        """
        return self.operate_fail_step(3)

    def retry_all(self):
        """
        全部重试
        @return:
        """
        return self.operate_fail_step(8)
