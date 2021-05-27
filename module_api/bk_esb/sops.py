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

from adapter.api import SopsApi


class SOPS:
    """
    Gcloud 3.0 接口
    """
    def get_template_list(self, bk_username, bk_biz_id, template_source="business"):
        """
        查询业务下的模板列表
        :param bk_username: 用户名
        :param bk_biz_id: 业务ID
        :param template_source: business common
        :return:
        {
            "category": "Other",
            "edit_time": "2018-04-23 17:30:48 +0800",
            "create_time": "2018-04-23 17:26:40 +0800",
            "name": "快速执行脚本",
            "bk_biz_id": "2",
            "creator": "admin",
            "bk_biz_name": "蓝鲸",
            "id": 32,
            "editor": "admin"
        }
        """
        kwargs = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "template_source": template_source,
        }
        response = SopsApi.get_template_list(kwargs, raw=True)
        return response

    def get_template_info(
            self,
            bk_username,
            bk_biz_id,
            template_id,
            template_source="business",
    ):
        """
        查看模版信息
        :param bk_username:
        :param bk_biz_id:
        :param template_id: 模版ID
        :param template_source:
        :return:
        """
        kwargs = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "template_id": template_id,
            "template_source": template_source,
        }
        response = SopsApi.get_template_info(kwargs, raw=True)
        return response

    def get_task_status(self, bk_username, bk_biz_id, task_id):
        """
        查询任务执行状态
            CREATED	未执行
            RUNNING	执行中
            FAILED	失败
            SUSPENDED	暂停
            REVOKED	已终止
            FINISHED	已完成
        :param bk_username:
        :param bk_biz_id:
        :param task_id: string/int 任务ID
        :return:
            status, start_time, end_time
        """
        kwargs = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "template_id": task_id,
        }
        response = SopsApi.get_task_status(kwargs, raw=True)
        status = "1"
        start_time = ""
        end_time = ""
        if response["result"]:
            data = response["data"]
            state = data.get("state", "")
            start_time = data.get("start_time", "")
            end_time = data.get("finish_time", "")
            if state == "FAILED":
                status = "3"
            elif state == "FINISHED":
                status = "2"
            elif state == "REVOKED":
                status = "5"
            elif state in ["CREATED", "RUNNING", "SUSPENDED"]:
                status = "1"

        return status, start_time, end_time

    def get_template_schemes(self, bk_biz_id, template_id, template_source="business"):
        """
        获取模板的执行方案列表
        """

        kwargs = {
            "bk_biz_id": bk_biz_id,
            "template_id": template_id,
            "template_source": template_source,
        }
        response = SopsApi.get_template_schemes_api(kwargs, raw=True)
        return response


class SOPSGW:
    """
    标准运维网官API
    """

    def get_template_list(self, bk_biz_id, template_source="business"):
        """
        查询业务下的模板列表
        :param bk_username: 用户名
        :param bk_biz_id: 业务ID
        :param template_source: business common
        :return:
        {
            "category": "Other",
            "edit_time": "2018-04-23 17:30:48 +0800",
            "create_time": "2018-04-23 17:26:40 +0800",
            "name": "快速执行脚本",
            "bk_biz_id": "2",
            "creator": "admin",
            "bk_biz_name": "蓝鲸",
            "id": 32,
            "editor": "admin"
        }
        """
        kwargs = {
            "bk_biz_id": bk_biz_id,
            "template_source": template_source,
        }
        response = SopsApi.get_template_list_api(kwargs, raw=True)
        return response

    def get_template_schemes(self, bk_biz_id, template_id, template_source="business"):
        """
        获取模板的执行方案列表
        """

        kwargs = {
            "bk_biz_id": bk_biz_id,
            "template_id": template_id,
            "template_source": template_source,
        }
        response = SopsApi.get_template_schemes_api(kwargs, raw=True)
        return response
