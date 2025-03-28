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
from common.constants import TaskExecStatus

sops_instance_status_map = {
    "CREATED": TaskExecStatus.INIT.value,  # 未执行
    "RUNNING": TaskExecStatus.RUNNING.value,  # 执行中
    "FAILED": TaskExecStatus.FAIL.value,  # 失败
    "FINISHED": TaskExecStatus.SUCCESS.value,  # 已完成
    "SUSPENDED": TaskExecStatus.SUSPENDED.value,  # 暂停
    "REVOKED": TaskExecStatus.REMOVE.value,  # 已终止
}


class SOPS:
    """
    标准运维组件API
    """

    @classmethod
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

    @classmethod
    def get_template_info(self, bk_username, bk_biz_id, template_id, template_source="business"):
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

    @classmethod
    def preview_task_tree(cls, bk_username, bk_biz_id, template_id, exclude_task_nodes_id):
        """
        预览模板创建后生成的任务树
        :param bk_username:
        :param bk_biz_id:
        :param template_id: 模版ID
        :param exclude_task_nodes_id: 需要移除的可选节点 ID 列表
        :return:
        """
        kwargs = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "template_id": template_id,
            "exclude_task_nodes_id": exclude_task_nodes_id,
        }
        response = SopsApi.preview_task_tree(kwargs, raw=True)
        return response

    @classmethod
    def get_task_status(self, bk_username: str, bk_biz_id: int, task_id: str):
        """
        查询任务执行状态
        :param bk_username:
        :param bk_biz_id:
        :param task_id: string/int 任务ID
        :return:
        """
        params = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "task_id": task_id,
        }
        sops_task_ret = SopsApi.get_task_status(params, raw=True)
        data = sops_task_ret.get("data", None)
        status = data.get("state", "")
        return {
            "ok": data is not None,
            "status": sops_instance_status_map.get(status, "1"),
            "data": data,
        }

    @classmethod
    def get_task_detail(cls, bk_username: str, bk_biz_id: int, task_id: str):
        """查询任务执行详情
        :param bk_username: 用户名
        :param bk_biz_id:   所属业务ID
        :param task_id:     任务ID
        :return:
        """
        kwargs = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "task_id": task_id,
        }
        sops_task_ret = SopsApi.get_task_detail(kwargs, raw=True)
        return sops_task_ret.get("data")

    @classmethod
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

    @classmethod
    def get_task_node_detail(cls, bk_username: str, bk_biz_id: int, task_id: str, node_id: str):
        """
        获取节点详情
        """
        kwargs = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "task_id": task_id,
            "node_id": node_id,
        }
        response = SopsApi.get_task_node_detail(kwargs, raw=True)
        return response

    @classmethod
    def operate_task(cls, bk_username: str, bk_biz_id: int, task_id: str, action: str):
        """
        操作任务
        """
        params = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "task_id": task_id,
            "action": action,
        }
        rsp = SopsApi.operate_task(params, raw=True)
        return rsp

    @classmethod
    def operate_node(cls, bk_username: str, bk_biz_id: int, task_id: str, node_id: str, action: str):
        """
        操作节点
        """
        params = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "task_id": task_id,
            "node_id": node_id,
            "action": action,
        }
        rsp = SopsApi.operate_node(params, raw=True)
        return rsp

    @classmethod
    def node_callback(
        cls, bk_username: str, bk_biz_id: int, task_id: str, node_id: str, action: str, callback_data=dict, scope=""
    ):
        """
        节点回调
        """
        params = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "task_id": task_id,
            "node_id": node_id,
            "action": action,
            "callback_data": callback_data,
            "scope": scope,
        }
        rsp = SopsApi.node_callback(params, raw=True)
        return rsp

    @classmethod
    def get_task_list(cls, bk_username: str, bk_biz_id: int, **kwargs):
        """
        获取任务列表
        """
        params = {"bk_username": bk_username, "bk_biz_id": bk_biz_id, **kwargs}
        rsp = SopsApi.get_task_list(params, raw=True)
        return rsp

    @classmethod
    def get_tasks_status(cls, bk_username: str, bk_biz_id: int, task_id_list: list):
        """
        批量获取任务状态
        """
        params = {
            "bk_username": bk_username,
            "bk_biz_id": bk_biz_id,
            "task_id_list": task_id_list,
        }
        rsp = SopsApi.get_tasks_status(params, raw=True)
        return rsp

    @classmethod
    def get_user_project_list(cls, bk_username: str):
        """
        获取用户有权限的项目列表
        """
        params = {
            "bk_username": bk_username,
        }
        rsp = SopsApi.get_user_project_list(params, raw=True)
        return rsp
