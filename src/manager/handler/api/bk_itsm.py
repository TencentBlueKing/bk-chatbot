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
import sys
from typing import Dict, List

from common.constants import TaskExecStatus

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from adapter.api import BkITSMApi

itsm_instance_status_map = {
    "CREATED": TaskExecStatus.INIT.value,  # 未执行
    "RUNNING": TaskExecStatus.RUNNING.value,  # 执行中
    "FAILED": TaskExecStatus.FAIL.value,  # 失败
    "FINISHED": TaskExecStatus.SUCCESS.value,  # 已完成
    "SUSPENDED": TaskExecStatus.SUSPENDED.value,  # 暂停
    "TERMINATED": TaskExecStatus.REMOVE.value,  # 已终止
}


class Field(TypedDict):
    """
    添加单据的字段信息
    """

    key: str
    value: str


class Meta(TypedDict):
    callback_url: str
    state_processors: Dict[str, str]


class BkITSM:
    @classmethod
    def create_ticket(
        self, service_id: int, creator: str, fields: List[Field], meta: Meta, fast_approval: bool = False
    ):
        """
        创建单据
        """
        params = {
            "service_id": service_id,
            "creator": creator,
            "fields": fields,
            "fast_approval": fast_approval,
            "meta": meta,
        }
        ret = BkITSMApi.create_ticket(params=params, raw=True)
        return ret

    @classmethod
    def token_verify(self, token: str):
        """
        token校验
        """
        params = {"token": token}
        ret = BkITSMApi.token_verify(params=params, raw=True)
        return ret

    @classmethod
    def ticket_approval_result(cls, sn_list: List[str]):
        params = {"sn": sn_list}
        ret = BkITSMApi.ticket_approval_result(params=params, raw=True)
        return ret

    @classmethod
    def get_services(cls):
        ret = BkITSMApi.get_services(raw=True)
        return ret

    @classmethod
    def get_service_detail(cls, service_id):
        params = {"service_id": service_id}
        ret = BkITSMApi.get_service_detail(params=params, raw=True)
        return ret

    @classmethod
    def get_ticket_status(cls, bk_username: str, task_id: str):
        """
        查询单据执行状态
        :param bk_username:
        :param task_id: string/int 任务ID
        :return:
        """
        params = {
            "bk_username": bk_username,
            "sn": task_id,
        }
        itsm_task_ret = BkITSMApi.get_ticket_status(params, raw=True)
        data = itsm_task_ret.get("data", {})
        current_status = data.get("current_status", "")
        return {
            "ok": data is not None,
            "status": itsm_instance_status_map.get(current_status, 1),
            "data": data,
        }

    @classmethod
    def get_ticket_info(cls, bk_username: str, task_id: str):
        params = {
            "bk_username": bk_username,
            "sn": task_id,
        }
        ret = BkITSMApi.get_ticket_info(params=params, raw=True)
        return ret.get("data")
