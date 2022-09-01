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
import datetime
import logging
import math
from celery.task import task

from src.manager.handler.api.bk_job import JOB
from src.manager.handler.api.bk_sops import SOPS
from src.manager.module_notice.handler.notice import Notice
from src.manager.module_biz.handlers.platform_task import parse_job_task_tree, parse_sops_pipeline_tree
from src.manager.module_notice.handler.notice_cache import get_notice_group_data
from src.manager.module_notice.models import TaskBroadcast
from src.manager.module_notice.handler.deal_boardcast_msg import OriginalBroadcast

from common.constants import TAK_PLATFORM_JOB, TAK_PLATFORM_SOPS, TASK_EXECUTE_STATUS_DICT, TaskExecStatus

logger = logging.getLogger("celery")

BROADCAST_LADDER = [5, 10, 20, 40, 60]

TASK_FINISHED_STATUS = {
    TASK_EXECUTE_STATUS_DICT[TaskExecStatus.REMOVE.value],
    TASK_EXECUTE_STATUS_DICT[TaskExecStatus.SUCCESS.value],
}


@task
def task_broadcast(broadcast_id):
    logger.info(f"[task_broadcast][info][broadcast_id={broadcast_id}] start broadcast")
    broadcast_obj = TaskBroadcast.objects.get(pk=broadcast_id)
    operator = broadcast_obj.start_user
    biz_id = broadcast_obj.biz_id
    task_id = broadcast_obj.task_id
    session_info = broadcast_obj.session_info
    share_group_list = broadcast_obj.share_group_list
    if broadcast_obj.is_stop:
        return

    if broadcast_obj.platform == TAK_PLATFORM_JOB:
        task_info = JOB().get_job_instance_status(operator, biz_id, task_id).get("data")
        parse_result = parse_job_task_tree(task_info, is_parse_all=False)

    if broadcast_obj.platform == TAK_PLATFORM_SOPS:
        task_info = SOPS().get_task_detail(operator, biz_id, task_id)
        status_info = SOPS().get_task_status(operator, biz_id, task_id).get("data")
        parse_result = parse_sops_pipeline_tree(task_info, status_info, is_parse_all=False)

    parse_result.update({"broadcast_id": broadcast_id})

    step_data = parse_result.get("step_data")
    current_step = step_data[math.floor(len(step_data) / 2)]

    now = datetime.datetime.now()
    if current_step["step_id"] == broadcast_obj.step_id and current_step["step_status"] == broadcast_obj.step_status:
        if now > datetime.datetime.strptime(broadcast_obj.next_broadcast_time, "%Y-%m-%d %H:%M:%S"):
            is_send_msg = True
            broadcast_ladder_index = (
                broadcast_obj.broadcast_num - 1 if broadcast_obj.broadcast_num - 1 < len(BROADCAST_LADDER) else -1
            )
            broadcast_obj.broadcast_num = broadcast_obj.broadcast_num + 1
            broadcast_obj.next_broadcast_time = now + datetime.timedelta(
                minutes=BROADCAST_LADDER[broadcast_ladder_index]
            )
            broadcast_obj.save()

        else:
            is_send_msg = False
    else:
        is_send_msg = True
        broadcast_obj.step_id = current_step["step_id"]
        broadcast_obj.step_status = current_step["step_status"]
        broadcast_obj.broadcast_num = 1
        broadcast_obj.next_broadcast_time = now
        broadcast_obj.save()

    if is_send_msg and session_info:
        print("curl bk_chat wit parse_result")

    if is_send_msg and share_group_list:
        origin_obj = OriginalBroadcast(parse_result)
        notice_groups = get_notice_group_data(share_group_list)
        for notice_group in notice_groups:
            msg_type, msg_content = getattr(origin_obj, notice_group.get("im").lower(), ("text", "解析步骤出错,请联系管理员"))
            notice = Notice(
                notice_group.get("im"), msg_type, msg_content, notice_group.get("receiver"), notice_group.get("headers")
            )
            result = notice.send()
            if not result["result"]:
                logger.error(
                    "[task_broadcast][error][broadcast_id={}][message={}]".format(broadcast_id, result["message"])
                )
    logger.info(f"[task_broadcast][info][broadcast_id={broadcast_id}] finish broadcast")
    if parse_result["task_status"] not in TASK_FINISHED_STATUS:
        task_broadcast.apply_async(kwargs={"broadcast_id": broadcast_obj.id}, countdown=60)
