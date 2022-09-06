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
    TaskExecStatus,
    TAK_PLATFORM_JOB,
    TAK_PLATFORM_SOPS,
)
from src.manager.handler.api.bk_sops import sops_instance_status_map
from src.manager.handler.api.bk_job import job_instance_status_map

TASK_STATUS_INIT = {
    TaskExecStatus.INIT.value,
}
TASK_STATUS_UNFINISHED = {
    TaskExecStatus.RUNNING.value,
    TaskExecStatus.FAIL.value,
    TaskExecStatus.SUSPENDED.value,
    TaskExecStatus.REMOVE.value,
}
TASK_STATUS_SUCCESS = {TaskExecStatus.SUCCESS.value}
# 标准运维除过汇聚网关的网关
SOPS_EXEC_GATEWAYS = {"ExclusiveGateway", "ParallelGateway", "ConditionalParallelGateway"}

# 可能存在循环的网关
SOPS_CYCLE_GATEWAYS = {"ExclusiveGateway", "ConditionalParallelGateway"}
BKAPP_JOB_HOST = os.getenv("BKAPP_JOB_HOST", "")

MAX_RANGE_NUM = 500

# 网关之后最多经过多少个节点出现汇聚节点
GATEWAY_MAX_RANGE_NUM = 30


def get_converge_node_id(first_flow_id, second_flow_id, flows, nodes):
    first_exec_node = []
    second_exec_node = []
    converge_node_id = "converge_node_id"
    for range_index in range(1, GATEWAY_MAX_RANGE_NUM):
        first_flow = flows.get(first_flow_id)
        if first_flow:
            first_flow_node_id = first_flow["target"]
            if first_flow_node_id in second_exec_node:
                converge_node_id = first_flow_node_id
                break
            first_exec_node.append(first_flow_node_id)
            first_flow_node_outgoing = nodes.get(first_flow_node_id).get("outgoing")
            first_flow_id = (
                first_flow_node_outgoing if isinstance(first_flow_node_outgoing, str) else first_flow_node_outgoing[0]
            )

        second_flow = flows.get(second_flow_id)
        if second_flow:
            second_flow_node_id = second_flow["target"]
            if second_flow_node_id in first_exec_node:
                converge_node_id = second_flow_node_id
                break
            second_exec_node.append(second_flow_node_id)
            second_flow_node_outgoing = nodes.get(second_flow_node_id).get("outgoing")
            second_flow_id = (
                second_flow_node_outgoing
                if isinstance(second_flow_node_outgoing, str)
                else second_flow_node_outgoing[0]
            )
    return converge_node_id


def judge_cycle_flow(flow_id, flows, nodes):
    cycle_exec_node_id_list = []

    def _judge_cycle_flow(_flow_id):
        for range_index in range(1, GATEWAY_MAX_RANGE_NUM):
            flow = flows.get(_flow_id)
            if not flow:
                break
            flow_node_id = flow["target"]
            if flow_node_id in cycle_exec_node_id_list:
                return True
            cycle_exec_node_id_list.append(flow_node_id)
            flow_node_outgoing = nodes.get(flow_node_id).get("outgoing")
            if isinstance(flow_node_outgoing, str):
                _flow_id = flow_node_outgoing
            elif isinstance(flow_node_outgoing, list):
                for _outgoing in flow_node_outgoing:
                    return _judge_cycle_flow(_outgoing)
        return False

    is_cycle = _judge_cycle_flow(flow_id)

    return is_cycle


def deal_cycle_flow(gateway_node, node_exec_list, flows, nodes):
    def _deal_cycle_flow(_flow_id):
        for range_index in range(1, GATEWAY_MAX_RANGE_NUM):
            node_exec_id_list = [n["id"] for n in node_exec_list]
            flow = flows.get(_flow_id)
            if not flow:
                break
            source_node_id = flow["source"]
            if source_node_id not in node_exec_id_list:
                node_exec_list.append({"id": source_node_id, "many_flows": True})
            else:
                break
            node_incoming = nodes.get(source_node_id).get("incoming")
            if isinstance(node_incoming, str):
                _flow_id = node_incoming
            elif isinstance(node_incoming, list):
                for _incoming in node_incoming:
                    _deal_cycle_flow(_incoming)

    for flow_id in gateway_node.get("incoming"):
        _deal_cycle_flow(flow_id)


def parse_sops_node_order(pipeline_tree):
    start_event = pipeline_tree.get("start_event")
    end_event = pipeline_tree.get("end_event")
    flows = pipeline_tree.get("flows")
    gateways = pipeline_tree.get("gateways", {})
    activities = pipeline_tree.get("activities", {})
    nodes = {
        **gateways,
        **activities,
        start_event.get("id"): start_event,
        end_event.get("id"): end_event,
    }
    node_exec_list = []

    def _parse_sops_node_order(next_flow_id, end_node_id, many_flows=False, end_node_many_flows=False):
        for _ in range(1, MAX_RANGE_NUM):
            if isinstance(next_flow_id, str):
                flow = flows.get(next_flow_id)
                target_node_id = flow["target"]
            elif isinstance(next_flow_id, list):
                converge_flow_id_list = []
                for _flow_id in next_flow_id:
                    is_cycle = judge_cycle_flow(_flow_id, flows, nodes)
                    if not is_cycle:
                        converge_flow_id_list.append(_flow_id)

                if len(converge_flow_id_list) >= 2:
                    converge_node_id = get_converge_node_id(
                        converge_flow_id_list[0], converge_flow_id_list[1], flows, nodes
                    )
                    for _flow_id in converge_flow_id_list:
                        _parse_sops_node_order(_flow_id, converge_node_id, True, False)
                        node_exec_list.pop()
                    target_node_id = converge_node_id
                elif len(converge_flow_id_list) == 1:
                    flow = flows.get(converge_flow_id_list[0])
                    target_node_id = flow["target"]

            if target_node_id in [n["id"] for n in node_exec_list]:
                break

            if target_node_id == end_node_id:
                node_exec_list.append({"id": target_node_id, "many_flows": end_node_many_flows})
                break
            elif isinstance(next_flow_id, list) and len(next_flow_id) == 1:
                node_exec_list.append({"id": target_node_id, "many_flows": True})
            else:
                node_exec_list.append({"id": target_node_id, "many_flows": many_flows})

            current_node = nodes.get(target_node_id)
            if current_node["type"] in SOPS_CYCLE_GATEWAYS:
                deal_cycle_flow(current_node, node_exec_list, flows, nodes)
            next_flow_id = current_node.get("outgoing")

    _parse_sops_node_order(start_event.get("outgoing"), end_event.get("id"), False, False)

    return node_exec_list


def parse_sops_pipeline_tree(task_info, status_info, is_parse_all=False):
    pipeline_tree = task_info.get("pipeline_tree")
    parse_result = [None]

    def _unfold_pipeline_tree(pipeline_data, status_data, parse_data, parent_step_index_list):
        node_info = {
            **pipeline_data.get("activities", {}),
            **pipeline_data.get("gateways", {}),
        }
        node_exec_list = parse_sops_node_order(pipeline_data)

        current_step_index_list = parent_step_index_list + [0, ".", 0, "-"]
        for index, _node in enumerate(node_exec_list):
            node_id = _node["id"]
            node = node_info.get(node_id)

            if not node:
                continue

            current_task_state = sops_instance_status_map[status_info.get("state")]
            if current_task_state in TASK_STATUS_SUCCESS:
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

            if node["type"] == "ConvergeGateway":
                continue

            if _node["many_flows"]:
                current_step_index_list[-2] += 1
            else:
                current_step_index_list[-4] += 1
                current_step_index_list[-2] = 0

            if node["type"] in SOPS_EXEC_GATEWAYS:
                continue

            current_step_index = "".join([str(i) for i in current_step_index_list[:-1]])

            node_start_time = node_status_info.get("start_time")
            node_finish_time = node_status_info.get("finish_time")
            current_parse_data = {
                "step_name": node["name"],
                "step_index": current_step_index,
                "step_id": node_id,
                "step_duration": node_status_info.get("elapsed_time") or 1,
                "step_status": TASK_EXECUTE_STATUS_DICT[node_state],
                "step_status_color": TASK_EXEC_STATUS_COLOR_DICT[node_state],
                "start_time": node_start_time and node_start_time.strip(" +0800"),
                "finish_time": node_finish_time and node_finish_time.strip(" +0800"),
            }

            parse_data.append(current_parse_data)
            if node["type"] == "SubProcess":
                if node_status_info.get("children"):
                    _unfold_pipeline_tree(
                        node["pipeline"], node_status_info.get("children"), parse_data, current_step_index_list
                    )

    _unfold_pipeline_tree(pipeline_tree, status_info.get("children"), parse_result, [])
    running_index = parse_result[0]
    parse_result = parse_result[1:]
    total_step_num = len(parse_result)
    task_state = sops_instance_status_map[status_info.get("state")]
    if task_state in TASK_STATUS_INIT:
        current_step_num = 0
    elif task_state in TASK_STATUS_SUCCESS:
        current_step_num = total_step_num
    else:
        for index, item in enumerate(parse_result):
            if item["step_status"] in {"执行中", "执行失败"}:
                current_step_num = index + 1
                break

    if not is_parse_all:
        if task_state in TASK_STATUS_INIT:
            parse_result = parse_result[:5]
        if task_state in TASK_STATUS_UNFINISHED:
            _start = running_index - 2 if running_index - 2 > 0 else 0
            _end = running_index + 3
            parse_result = parse_result[_start:_end]
        if task_state in TASK_STATUS_SUCCESS:
            parse_result = parse_result[-5:]

    start_time = status_info.get("start_time")
    finish_time = status_info.get("finish_time")
    exec_state = sops_instance_status_map[status_info.get("state")]
    data = {
        "task_name": "[标准运维] {}".format(status_info.get("name")),
        "task_status": TASK_EXECUTE_STATUS_DICT[exec_state],
        "task_status_color": TASK_EXEC_STATUS_COLOR_DICT[exec_state],
        "task_duration": status_info.get("elapsed_time") or 1,
        "step_data": parse_result,
        "total_step_num": total_step_num,
        "current_step_num": current_step_num,
        "start_time": start_time and start_time.strip(" +0800"),
        "finish_time": finish_time and finish_time.strip(" +0800"),
        "task_url": task_info.get("task_url"),
        "task_platform": TAK_PLATFORM_SOPS,
        "task_id": task_info.get("id"),
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

        total_time = step_instance.get("total_time") or 1
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
    parse_result = [{**item, "step_num": index + 1} for index, item in enumerate(parse_result)]
    total_step_num = len(parse_result)

    if exec_status in TASK_STATUS_INIT:
        current_step_num = 0
    elif exec_status in TASK_STATUS_SUCCESS:
        current_step_num = total_step_num
    else:
        for index, item in enumerate(parse_result):
            if item["step_status"] in {"执行中", "执行失败", "执行终止"}:
                current_step_num = index + 1
                break

    if not is_parse_all:
        if exec_status in TASK_STATUS_INIT:
            parse_result = parse_result[:5]
        if exec_status in TASK_STATUS_UNFINISHED:
            _start = running_index - 2 if running_index - 2 > 0 else 0
            _end = running_index + 3
            parse_result = parse_result[_start:_end]
        if exec_status in TASK_STATUS_SUCCESS:
            parse_result = parse_result[-5:]

    total_time = job_instance_info.get("total_time") or 1
    if not total_time:
        total_time = (time.time() * 1000) - start_time
    data = {
        "task_name": "[作业平台] {}".format(job_instance_info.get("name")),
        "task_id": job_instance_info.get("job_instance_id"),
        "task_platform": TAK_PLATFORM_JOB,
        "total_step_num": total_step_num,
        "current_step_num": current_step_num,
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
