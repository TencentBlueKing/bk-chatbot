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

import asyncio
import copy

from common.drf.exceptions import HttpRequestError, HttpResultError
from src.manager.handler.api.bk_sops import SOPS


class BkSops:
    def __init__(self, username, biz_id, task_id):
        """
        @param username: 执行用户
        @param biz_id:   业务id
        @param task_id:  任务id
        """
        self.username = username
        self.biz_id = biz_id
        self.task_id = task_id
        self.task_detail = None

    def get_fail_node(self):
        """
        获取失败节点
        @return:
        """
        ret = SOPS.get_task_status(
            bk_username=self.username,
            bk_biz_id=self.biz_id,
            task_id=self.task_id,
        )
        children = ret.get("data", {}).get("children", {})
        # 失败节点ID
        fail_node_ids = list(
            map(
                lambda x: x.get("id"),
                filter(lambda value: value.get("state") == "FAILED", children.values()),
            )
        )
        return fail_node_ids

    def _operate_task(self, action: str):
        """
        操作任务
        @param action:
        @return:
        """
        return SOPS.operate_task(
            bk_username=self.username,
            bk_biz_id=self.biz_id,
            task_id=self.task_id,
            action=action,
        )

    async def _operate_single_node(self, node_id, action):
        """

        @return:
        """
        ret = SOPS.operate_node(
            bk_username=self.username,
            bk_biz_id=self.biz_id,
            task_id=self.task_id,
            node_id=node_id,
            action=action,
        )
        return ret

    def _operate_much_node(self, node_ids, action):
        """
        操作节点
        @param node_ids:
        @param action:
        @return:
        """
        tasks = list(
            map(
                lambda node_id: self._operate_single_node(node_id, action),
                node_ids,
            )
        )
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
        ret_list, _ = loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

        # 结果处理
        for ret in ret_list:
            exception = ret.exception()
            if exception:
                raise HttpRequestError(exception)
            result = ret.result()
            if not result.get("result"):
                raise HttpResultError("操作节点存在失败")

    def _operate_node(self, node_id, action):
        """
        操作节点
        @param node_id: 节点id
        @param action:  操作
        @return:
        """
        node_ids = [node_id] if node_id else self.get_fail_node()
        return self._operate_much_node(node_ids, action=action)

    def get_task_status(self):
        """
        获取任务状态
        @return:
        """
        return SOPS.get_task_status(
            bk_username=self.username,
            bk_biz_id=self.biz_id,
            task_id=self.task_id,
        )

    def get_task_detail(self):
        """
        获取任务详情
        @return:
        """
        detail = SOPS.get_task_detail(
            bk_username=self.username,
            bk_biz_id=self.biz_id,
            task_id=self.task_id,
        )
        self.task_detail = copy.deepcopy(detail)
        return detail

    @property
    def task_uri(self):
        """
        获取任务地址
        @return:
        """
        if self.task_detail is None:
            self.get_task_detail()
        return self.task_detail.get("task_url")

    @property
    def params(self):
        """
        获取参数
        @return:
        """
        detail = self.get_task_detail()
        constants: dict = detail.get("constants")  # 请求参数
        # 获取参数
        param_list = list(
            map(
                lambda x: {
                    "name": x.get("name"),
                    "value": x.get("value"),
                },
                filter(lambda constant: constant.get("show_type") == "show", constants.values()),
            )
        )
        return param_list

    def revoke_task(self):
        """
        停止任务
        @return:
        """

        return self._operate_task(action="revoke")

    def pause_task(self):
        """
        暂停任务
        @return:
        """
        return self._operate_task(action="pause")

    def resume_task(self):
        """
        继续任务
        @return:
        """
        return self._operate_task(action="resume")

    def skip_node(self, node_id):
        """
        跳过节点
        @return:
        """
        return self._operate_node(node_id, action="skip")

    def retry_node(self, node_id):
        """
        重试节点
        @return:
        """

        return self._operate_node(node_id, action="retry")

    def callback_node(self):
        """
        回调节点
        @return:
        """
        pass
