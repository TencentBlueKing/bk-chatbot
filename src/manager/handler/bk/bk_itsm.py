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

import copy

from src.manager.handler.api.bk_itsm import BkITSM


class BkItsm:
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
        self.ticket_url = None

    def get_ticket_status(self):
        """
        获取单据状态
        @return:
        """
        ret = BkITSM.get_ticket_status(
            bk_username=self.username,
            task_id=self.task_id,
        )
        self.ticket_url = ret.get("data", {}).get("ticket_url")
        return ret

    def get_ticket_info(self):
        """
        获取单据详情
        @return:
        """
        if self.task_detail is not None:
            return self.task_detail

        detail = BkITSM.get_ticket_info(
            bk_username=self.username,
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
        if self.ticket_url is None:
            self.get_ticket_status()

        return self.ticket_url

    @property
    def params(self):
        """
        获取参数
        @return:
        """
        if self.task_detail is None:
            self.get_ticket_info()

        fields: dict = self.task_detail.get("fields")  # 请求参数
        # 获取参数
        param_list = [{"name": f["name"], "value": f["value"]} for f in fields]
        return param_list
