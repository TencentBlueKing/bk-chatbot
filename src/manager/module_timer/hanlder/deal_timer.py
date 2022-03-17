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

from common.constants import TIMER_BIZ_ID, TIMER_JOB_PLAN_ID, TIMER_USER_NAME
from handler.api.bk_job import JOB
from module_timer.models import TimerModel


def deal_timer(serializer) -> TimerModel:
    """
    定时任务处理逻辑
    """
    timer_obj: TimerModel = serializer.save()
    rsp = JOB.save_cron(
        bk_username=TIMER_USER_NAME,
        bk_biz_id=int(TIMER_BIZ_ID),
        job_plan_id=int(TIMER_JOB_PLAN_ID),
        id=timer_obj.job_timer_id,
        name=timer_obj.timer_name,
        expression=timer_obj.expression,
        execute_time=timer_obj.execute_time,
        timer_id=timer_obj.id,
    )

    result = rsp.get("result", False)
    if not result:
        raise ValueError(rsp.get("message", "调用定时任务接口异常"))
    job_timer_id = rsp.get("data", {}).get("id", None)
    if not isinstance(job_timer_id, int):
        raise TypeError("job_timer_id must is int")
    # 修改状态
    timer_obj.job_timer_id = job_timer_id
    timer_obj.save()
    # 定时任务类型修改
    if timer_obj.execute_time != "":
        timer_obj.timer_type = TimerModel.TimerType.ONCE.value
    if timer_obj.expression != "":
        timer_obj.timer_type = TimerModel.TimerType.REPEAT.value

    return timer_obj


def update_timer_status(id: int, status: int):
    """
    @param id:
    @param status:
    @return:
    """

    rsp = JOB.update_cron_status(
        bk_username=TIMER_USER_NAME,
        bk_biz_id=int(TIMER_BIZ_ID),
        id=id,
        status=status,
    )
    ok = rsp.get("result")
    if not ok:
        raise Exception("修改定时任务状态失败")
