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
import re
import datetime
import logging
import math
from celery.task import task

from src.manager.handler.api.bk_job import JOB
from src.manager.handler.api.bk_sops import SOPS
from src.manager.handler.api.bk_chat import BkChat
from src.manager.handler.api.devops import DevOps
from src.manager.module_notice.handler.notice import Notice
from src.manager.module_notice.constants import BROADCAST
from src.manager.module_biz.handlers.platform_task import (
    parse_job_task_tree,
    parse_sops_pipeline_tree,
    parse_devops_pipeline,
)
from src.manager.module_notice.handler.notice_cache import get_notice_group_data
from src.manager.module_notice.models import TaskBroadcast
from src.manager.module_notice.handler.deal_boardcast_msg import OriginalBroadcast, OriginalParamsBroadcast

from common.constants import (
    TAK_PLATFORM_JOB,
    TAK_PLATFORM_SOPS,
    TAK_PLATFORM_DEVOPS,
    TASK_EXECUTE_STATUS_DICT,
    TaskExecStatus,
)

logger = logging.getLogger("celery")

TASK_FINISHED_STATUS = {
    TASK_EXECUTE_STATUS_DICT[TaskExecStatus.REMOVE.value],
    TASK_EXECUTE_STATUS_DICT[TaskExecStatus.SUCCESS.value],
}
BK_TIMING_DATE_REGX = re.compile(
    r"%s %s"
    % (
        r"^(((\d{3}[1-9]|\d{2}[1-9]\d{1}|\d{1}[1-9]\d{2}|[1-9]\d{3}))|"
        r"(29/02/((\d{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))))-"
        r"((0[13578]|1[02])-((0[1-9]|[12]\d|3[01]))|"
        r"((0[469]|11)-(0[1-9]|[12]\d|30))|(02)-(0[1-9]|[1]\d|2[0-8]))",
        r"((0|[1])\d|2[0-3]):(0|[1-5])\d:(0|[1-5])\d$",
    )
)
BK_TIMING_SECONDS_REGX = re.compile(r"^\d+$")
BKAPP_JOB_HOST = os.getenv("BKAPP_JOB_HOST", "")
BKAPP_DEVOPS_HOST = os.getenv("BKAPP_DEVOPS_HOST", "")
BK_BROADCAST_SLEEP_PLUGIN_CODE = os.getenv("BK_BROADCAST_SLEEP_PLUGIN_CODE", "").split(",")


@task
def task_broadcast(broadcast_id):
    logger.info(f"[task_broadcast][info][broadcast_id={broadcast_id}] start broadcast")
    try:
        broadcast_obj = TaskBroadcast.objects.get(pk=broadcast_id)
        operator = broadcast_obj.start_user
        biz_id = broadcast_obj.biz_id
        task_id = broadcast_obj.task_id
        custom_task_name = broadcast_obj.custom_task_name
        session_info = broadcast_obj.session_info
        extra_notice_info = broadcast_obj.extra_notice_info
        share_group_list = broadcast_obj.share_group_list
        task_platform = broadcast_obj.platform
        broadcast_ladder_list = broadcast_obj.ladder_list
        current_step_detail = {}
        if broadcast_obj.is_stop:
            return

        if task_platform == TAK_PLATFORM_JOB:
            task_info = JOB().get_job_instance_status(operator, biz_id, task_id).get("data")
            parse_result = parse_job_task_tree(task_info, is_parse_all=False)

        if task_platform == TAK_PLATFORM_SOPS:
            task_info = SOPS().get_task_detail(operator, biz_id, task_id)
            status_info = SOPS().get_task_status(operator, biz_id, task_id).get("data")
            parse_result = parse_sops_pipeline_tree(task_info, status_info, is_parse_all=False)
            if custom_task_name:
                parse_result["task_name"] = "[标准运维] {}".format(custom_task_name)
            current_step_detail = parse_result.get("current_step_detail", {})

        if task_platform == TAK_PLATFORM_DEVOPS:
            build_detail = DevOps().app_build_detail(
                operator,
                broadcast_obj.devops_project_id,
                broadcast_obj.devops_pipeline_id,
                broadcast_obj.devops_build_id,
            )
            parse_result = parse_devops_pipeline(broadcast_obj.devops_project_id, build_detail, is_parse_all=False)
            parse_result.update({"task_id": task_id})

        step_data = parse_result.get("step_data")
        current_step = step_data[math.floor(len(step_data) / 2)]

        if task_platform == TAK_PLATFORM_SOPS:
            _current_steps = [step for step in step_data if step["step_id"] == current_step_detail["step_id"]]

            if _current_steps:
                current_step = _current_steps[0]

        if current_step["step_duration"] >= 60 * 60 * 24 * 3:
            broadcast_obj.is_stop = True
            broadcast_obj.save()

        now = datetime.datetime.now()
        if (
            current_step["step_id"] == broadcast_obj.step_id
            and current_step["step_status"] == broadcast_obj.step_status
        ):
            if now > datetime.datetime.strptime(broadcast_obj.next_broadcast_time, "%Y-%m-%d %H:%M:%S"):
                is_send_msg = True
                broadcast_ladder_index = (
                    broadcast_obj.broadcast_num - 1
                    if broadcast_obj.broadcast_num - 1 < len(broadcast_ladder_list)
                    else -1
                )
                broadcast_obj.broadcast_num = broadcast_obj.broadcast_num + 1
                broadcast_obj.next_broadcast_time = now + datetime.timedelta(
                    minutes=broadcast_ladder_list[broadcast_ladder_index]
                )
                broadcast_obj.save()

            else:
                is_send_msg = False

            # 如果是标准运维暂停节点,只是第一次发送消息
            if current_step_detail.get("plugin_code") in BK_BROADCAST_SLEEP_PLUGIN_CODE:
                is_send_msg = False

            # 如果是标准运维任务状态失败,只是第一次发送消息
            if current_step["step_status"] == "执行失败":
                is_send_msg = False

        else:
            is_send_msg = True
            broadcast_obj.step_id = current_step["step_id"]
            broadcast_obj.step_status = current_step["step_status"]
            broadcast_obj.broadcast_num = 1
            broadcast_obj.next_broadcast_time = now + datetime.timedelta(minutes=broadcast_ladder_list[0])
            broadcast_obj.save()

        if is_send_msg and session_info:
            parse_result.update(
                {
                    "broadcast_id": broadcast_id,
                    "session_info": session_info,
                    "start_user": operator,
                }
            )
            result = BkChat.send_broadcast(parse_result)
            if result["code"] != 0:
                logger.error(f"[task_broadcast][error][broadcast_id={broadcast_id}][result={result}]")

        if is_send_msg and share_group_list:
            origin_obj = OriginalBroadcast(parse_result)
            notice_groups = get_notice_group_data(share_group_list)
            for notice_group in notice_groups:
                kwargs = {
                    "im_platform": notice_group.get("im_platform"),
                    "biz_id": biz_id,
                    "msg_source": BROADCAST,
                    "group_name": notice_group.get("notice_group_name"),
                }
                msg_type, msg_content = getattr(origin_obj, notice_group.get("im").lower(), ("text", "解析步骤出错,请联系管理员"))
                notice = Notice(
                    notice_group.get("im"),
                    msg_type,
                    msg_content,
                    notice_group.get("receiver"),
                    notice_group.get("headers"),
                    **kwargs,
                )
                result = notice.send()
                if not result["result"]:
                    logger.error(f"[task_broadcast][error][broadcast_id={broadcast_id}][result={result}]")

        if is_send_msg and extra_notice_info:
            origin_obj = OriginalBroadcast(parse_result)
            msg_type, msg_content = getattr(origin_obj, "wework", ("text", "解析步骤出错,请联系管理员"))
            for _notice_info in extra_notice_info:
                kwargs = {
                    "im_platform": "企业微信",
                    "biz_id": biz_id,
                    "msg_source": BROADCAST,
                    "group_name": "附加通知人/群组",
                }
                notice = Notice("WEWORK", msg_type, msg_content, _notice_info, headers={}, **kwargs)
                result = notice.send()
                if not result["result"]:
                    logger.error(f"[task_broadcast][error][broadcast_id={broadcast_id}][result={result}]")

        logger.info(f"[task_broadcast][info][broadcast_id={broadcast_id}] finish broadcast")

        if (
            task_platform == TAK_PLATFORM_DEVOPS
            and broadcast_obj.step_status == "执行失败"
            and broadcast_obj.broadcast_num >= 3
        ):
            return

        if parse_result["task_status"] not in TASK_FINISHED_STATUS:
            # 如果是标准运维定时插件,则在定时结束前唤醒
            if task_platform == TAK_PLATFORM_SOPS and current_step_detail.get("plugin_code") == "sleep_timer":
                node_detail = SOPS().get_task_node_detail(operator, biz_id, task_id, current_step_detail.get("step_id"))
                bk_timing = node_detail.get("data", {}).get("inputs", {}).get("bk_timing", "")
                if bk_timing:
                    if BK_TIMING_DATE_REGX.match(str(bk_timing)):
                        eta = datetime.datetime.strptime(bk_timing, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(
                            seconds=20
                        )
                        task_broadcast.apply_async(kwargs={"broadcast_id": broadcast_obj.id}, eta=eta)
                        return
                    elif BK_TIMING_SECONDS_REGX.match(str(bk_timing)):
                        countdown = int(bk_timing) + 20
                        task_broadcast.apply_async(kwargs={"broadcast_id": broadcast_obj.id}, countdown=countdown)
                        return

            task_broadcast.apply_async(kwargs={"broadcast_id": broadcast_obj.id}, countdown=60)
    except Exception:
        logger.exception(f"[task_broadcast-error-broadcast_id-{broadcast_id}]")
        broadcast_obj = TaskBroadcast.objects.get(pk=broadcast_id)
        broadcast_obj.retry_num = broadcast_obj.retry_num + 1
        broadcast_obj.save()
        if broadcast_obj.retry_num <= 5:
            logger.warning(
                f"[task_broadcast][warn][broadcast_id={broadcast_id}] will retry [{broadcast_obj.retry_num}/5]"
            )
            task_broadcast.apply_async(kwargs={"broadcast_id": broadcast_id}, countdown=60)


@task
def task_params_broadcast(broadcast_id):
    logger.info(f"[task_params_broadcast][info][broadcast_id={broadcast_id}] start broadcast")
    try:
        broadcast_obj = TaskBroadcast.objects.get(pk=broadcast_id)
        operator = broadcast_obj.start_user
        biz_id = broadcast_obj.biz_id
        task_id = broadcast_obj.task_id
        custom_task_name = broadcast_obj.custom_task_name
        extra_notice_info = broadcast_obj.extra_notice_info
        share_group_list = broadcast_obj.share_group_list
        task_platform = broadcast_obj.platform
        if task_platform == TAK_PLATFORM_JOB:
            params_info = JOB().get_job_instance_global_var_value(operator, biz_id, task_id)
            task_info = JOB().get_job_instance_status(operator, biz_id, task_id).get("data")
            job_instance_id = params_info.get("job_instance_id")
            step_instance_var_list = params_info.get("step_instance_var_list", [])
            params_result = {}
            global_var_list = [var for s in step_instance_var_list for var in s["global_var_list"]]
            for var in global_var_list:
                params_result.update({var["name"]: {"params_name": var["name"], "params_value": var["value"]}})
            task_params = list(params_result.values())
            task_url = f"{BKAPP_JOB_HOST}/biz/{biz_id}/execute/task/{job_instance_id}"
            task_name = "[作业平台] {}".format(task_info.get("job_instance").get("name"))

        if task_platform == TAK_PLATFORM_SOPS:
            task_info = SOPS().get_task_detail(operator, biz_id, task_id)
            constants = task_info.get("constants")
            task_params = [
                {"params_name": v["name"], "params_value": v["value"]}
                for k, v in constants.items()
                if v["show_type"] == "show"
            ]
            task_url = task_info.get("task_url")
            task_name = "[标准运维] {}".format(task_info.get("name"))
            if custom_task_name:
                task_name = "[标准运维] {}".format(custom_task_name)

        if task_platform == TAK_PLATFORM_DEVOPS:
            build_info = DevOps().app_build_status(
                operator,
                broadcast_obj.devops_project_id,
                broadcast_obj.devops_pipeline_id,
                broadcast_obj.devops_build_id,
            )

            build_params = build_info.get("data", {}).get("buildParameters", [])
            task_params = [{"params_name": item["key"], "params_value": item["value"]} for item in build_params]
            task_url = "{}/console/pipeline/{}/{}/detail/{}".format(
                BKAPP_DEVOPS_HOST,
                broadcast_obj.devops_project_id,
                broadcast_obj.devops_pipeline_id,
                broadcast_obj.devops_build_id,
            )
            task_name = "[蓝盾] {}".format(build_info["data"]["variables"]["pipeline.name"])

        if share_group_list:
            origin_obj = OriginalParamsBroadcast(task_name, task_url, task_params)
            notice_groups = get_notice_group_data(share_group_list)
            for notice_group in notice_groups:
                kwargs = {
                    "im_platform": notice_group.get("im_platform"),
                    "biz_id": biz_id,
                    "msg_source": BROADCAST,
                    "group_name": notice_group.get("notice_group_name"),
                }
                msg_type, msg_content = getattr(origin_obj, notice_group.get("im").lower(), ("text", "解析参数出错,请联系管理员"))
                notice = Notice(
                    notice_group.get("im"),
                    msg_type,
                    msg_content,
                    notice_group.get("receiver"),
                    notice_group.get("headers"),
                    **kwargs,
                )
                result = notice.send()
                if not result["result"]:
                    logger.error(f"[task_params_broadcast][error][broadcast_id={broadcast_id}][result={result}]")

        if extra_notice_info:
            origin_obj = OriginalParamsBroadcast(task_name, task_url, task_params)
            msg_type, msg_content = getattr(origin_obj, "wework", ("text", "解析参数出错,请联系管理员"))
            for _notice_info in extra_notice_info:
                kwargs = {
                    "im_platform": "企业微信",
                    "biz_id": biz_id,
                    "msg_source": BROADCAST,
                    "group_name": "附加通知人/群组",
                }
                notice = Notice("WEWORK", msg_type, msg_content, _notice_info, headers={}, **kwargs)
                result = notice.send()
                if not result["result"]:
                    logger.error(f"[task_params_broadcast][error][broadcast_id={broadcast_id}][result={result}]")

    except Exception:
        logger.exception(f"[task_params_broadcast-error-broadcast_id-{broadcast_id}]")
