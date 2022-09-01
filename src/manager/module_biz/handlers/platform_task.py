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
import time

from common.constants import (
    TASK_EXECUTE_STATUS_DICT,
    TASK_EXEC_STATUS_COLOR_DICT,
    SOPS_GATEWAY_NODE_TYPE_MAP,
    TaskExecStatus,
)
from src.manager.handler.api.bk_sops import sops_instance_status_map
from src.manager.handler.api.bk_job import job_instance_status_map

TASK_STATUS_INIT = {
    TaskExecStatus.INIT.value,
}
TASK_STATUS_UNFINISHED = {TaskExecStatus.RUNNING.value, TaskExecStatus.FAIL.value, TaskExecStatus.SUSPENDED.value}
TASK_STATUS_FINISHED = {TaskExecStatus.REMOVE.value, TaskExecStatus.SUCCESS.value}
BKAPP_JOB_HOST = os.getenv("BKAPP_JOB_HOST", "")


def parse_sops_pipeline_tree(task_info, status_info, is_parse_all=False):
    pipeline_tree = task_info.get("pipeline_tree")
    parse_result = [None]

    def _unfold_pipeline_tree(pipeline_data, status_data, parse_data, parent_step_index_list):
        node_info = {
            **pipeline_data.get("activities", {}),
            **pipeline_data.get("gateways", {}),
        }
        location = pipeline_data.get("location", [])
        if location:
            location.insert(0, {})
            location.append({})
        current_step_index_list = parent_step_index_list + [0]
        for index, node in enumerate(location):
            if index == 0:
                start_event = pipeline_data.get("start_event")
                node_id = start_event.get("id")
                start_event.update({"name": "开始节点"})
                node = start_event
            elif index == len(location) - 1:
                end_event = pipeline_data.get("end_event")
                node_id = end_event.get("id")
                end_event.update({"name": "结束节点"})
                node = end_event
            else:
                node_id = node["id"]
                node = node_info.get(node_id)

            if not node:
                continue

            current_task_state = sops_instance_status_map[status_info.get("state")]
            if current_task_state in TASK_STATUS_FINISHED:
                default_status_info = {}
            else:
                default_status_info = {
                    "state": "CREATED",
                }

            node_status_info = status_data.get(node_id, default_status_info)

            if not node_status_info:
                continue
            node_state = sops_instance_status_map[node_status_info["state"]]

            if node_state in TASK_STATUS_UNFINISHED and parse_data[0] is None and node["type"] != "SubProcess":
                parse_data[0] = len(parse_data) - 1

            current_step_index_list[-1] += 1
            current_step_index = ".".join([str(i) for i in current_step_index_list])

            node_start_time = node_status_info.get("start_time")
            node_finish_time = node_status_info.get("finish_time")
            current_parse_data = {
                "step_name": node["name"],
                "step_index": current_step_index,
                "step_id": node_id,
                "step_duration": node_status_info.get("elapsed_time") or 0,
                "step_status": TASK_EXECUTE_STATUS_DICT[node_state],
                "step_status_color": TASK_EXEC_STATUS_COLOR_DICT[node_state],
                "start_time": node_start_time and node_start_time.strip(" +0800"),
                "finish_time": node_finish_time and node_finish_time.strip(" +0800"),
            }

            if node["type"] in SOPS_GATEWAY_NODE_TYPE_MAP.keys():
                name = ""
                if node["name"]:
                    name = f"-{name}"
                current_parse_data.update(
                    {
                        "step_name": "{}{}".format(SOPS_GATEWAY_NODE_TYPE_MAP[node["type"]], name),
                    }
                )

            parse_data.append(current_parse_data)
            if node["type"] == "SubProcess":
                if node_status_info.get("children"):
                    _unfold_pipeline_tree(
                        node["pipeline"], node_status_info.get("children"), parse_data, current_step_index_list
                    )

    _unfold_pipeline_tree(pipeline_tree, status_info.get("children"), parse_result, [1])
    running_index = parse_result[0]
    parse_result = parse_result[1:]
    task_state = sops_instance_status_map[status_info.get("state")]
    if not is_parse_all:
        if task_state in TASK_STATUS_INIT:
            parse_result = parse_result[:5]
        if task_state in TASK_STATUS_UNFINISHED:
            _start = running_index - 2 if running_index - 2 > 0 else 0
            _end = running_index + 3
            parse_result = parse_result[_start:_end]
        if task_state in TASK_STATUS_FINISHED:
            parse_result = parse_result[-5:]

    start_time = status_info.get("start_time")
    finish_time = status_info.get("finish_time")
    exec_state = sops_instance_status_map[status_info.get("state")]
    data = {
        "task_name": "[标准运维] {}".format(status_info.get("name")),
        "task_status": TASK_EXECUTE_STATUS_DICT[exec_state],
        "task_status_color": TASK_EXEC_STATUS_COLOR_DICT[exec_state],
        "task_duration": status_info.get("elapsed_time") or 0,
        "step_data": parse_result,
        "start_time": start_time and start_time.strip(" +0800"),
        "finish_time": finish_time and finish_time.strip(" +0800"),
        "task_url": task_info.get("task_url"),
    }
    return data


def parse_job_task_tree(task_info, is_parse_all=False):
    job_instance_info = task_info.get("job_instance")
    step_instance_list = task_info.get("step_instance_list")
    parse_result = []
    running_index = None
    for index, step_instance in enumerate(step_instance_list):
        exec_status = job_instance_status_map[step_instance["status"]]
        start_time = step_instance.get("start_time")
        finish_time = step_instance.get("end_time")
        if exec_status in TASK_STATUS_UNFINISHED and running_index is None:
            running_index = len(parse_result)

        total_time = step_instance.get("total_time") or 0
        if not total_time:
            total_time = (time.time() * 1000) - start_time
        parse_result.append(
            {
                "step_name": step_instance.get("name"),
                "step_index": f"1.{index + 1}",
                "step_id": str(step_instance.get("step_instance_id")),
                "step_duration": total_time / 1000,
                "step_status": TASK_EXECUTE_STATUS_DICT[exec_status],
                "step_status_color": TASK_EXEC_STATUS_COLOR_DICT[exec_status],
                "start_time": start_time
                and time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(start_time / 1000))),
                "finish_time": finish_time
                and time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(finish_time / 1000))),
            }
        )

    start_time = job_instance_info.get("start_time")
    finish_time = job_instance_info.get("end_time")
    exec_status = job_instance_status_map[job_instance_info["status"]]

    if not is_parse_all:
        if exec_status in TASK_STATUS_INIT:
            parse_result = parse_result[:5]
        if exec_status in TASK_STATUS_UNFINISHED:
            _start = running_index - 2 if running_index - 2 > 0 else 0
            _end = running_index + 3
            parse_result = parse_result[_start:_end]
        if exec_status in TASK_STATUS_FINISHED:
            parse_result = parse_result[-5:]
    total_time = job_instance_info.get("total_time") or 0
    if not total_time:
        total_time = (time.time() * 1000) - start_time
    data = {
        "task_name": "[作业平台] {}".format(job_instance_info.get("name")),
        "task_status": TASK_EXECUTE_STATUS_DICT[exec_status],
        "task_status_color": TASK_EXEC_STATUS_COLOR_DICT[exec_status],
        "task_duration": total_time / 1000,
        "step_data": parse_result,
        "start_time": start_time and time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(start_time / 1000))),
        "finish_time": finish_time and time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(finish_time / 1000))),
        "task_url": "{}/biz/{}/execute/task/{}".format(
            BKAPP_JOB_HOST, job_instance_info.get("bk_biz_id"), job_instance_info.get("job_instance_id")
        ),
    }
    return data
