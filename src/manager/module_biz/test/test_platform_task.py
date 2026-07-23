import importlib
import sys
import types
from copy import deepcopy

import pytest


@pytest.fixture(scope="module")
def parse_sops_pipeline_tree():
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("BKAPP_JOB_HOST", "http://job.example.com")
    monkeypatch.setenv("BKAPP_DEVOPS_HOST", "http://devops.example.com")

    # platform_task only needs the status mappings from these modules. Stubbing
    # the unrelated API clients keeps this parser unit test independent from
    # Django and the legacy deployment dependencies.
    adapter_api = types.ModuleType("adapter.api")
    adapter_api.SopsApi = object()
    monkeypatch.setitem(sys.modules, "adapter.api", adapter_api)

    bk_job = types.ModuleType("src.manager.handler.api.bk_job")
    bk_job.job_instance_status_map = {}
    monkeypatch.setitem(sys.modules, "src.manager.handler.api.bk_job", bk_job)

    devops = types.ModuleType("src.manager.handler.api.devops")
    devops.dev_ops_instance_status_map = {}
    monkeypatch.setitem(sys.modules, "src.manager.handler.api.devops", devops)

    module_names = [
        "src.manager.handler.api.bk_sops",
        "src.manager.module_biz.handlers.platform_task",
    ]
    for module_name in module_names:
        monkeypatch.delitem(sys.modules, module_name, raising=False)

    module = importlib.import_module("src.manager.module_biz.handlers.platform_task")
    yield module.parse_sops_pipeline_tree
    monkeypatch.undo()


def service(node_id, name):
    return {
        "id": node_id,
        "name": name,
        "type": "ServiceActivity",
        "component": {"code": "noop", "data": {}},
    }


def subprocess(node_id, name, pipeline):
    return {
        "id": node_id,
        "name": name,
        "type": "SubProcess",
        "pipeline": pipeline,
    }


def linear_pipeline(*raw_nodes):
    nodes = [deepcopy(node) for node in raw_nodes]
    flows = {}
    start = {"id": "start", "type": "EmptyStartEvent", "outgoing": "flow-0"}
    end = {"id": "end", "type": "EmptyEndEvent"}
    previous = start["id"]

    for index, node in enumerate(nodes):
        incoming = "flow-{}".format(index)
        outgoing = "flow-{}".format(index + 1)
        flows[incoming] = {"id": incoming, "source": previous, "target": node["id"]}
        node["incoming"] = incoming
        node["outgoing"] = outgoing
        previous = node["id"]

    final_flow = "flow-{}".format(len(nodes))
    flows[final_flow] = {"id": final_flow, "source": previous, "target": end["id"]}
    end["incoming"] = final_flow

    return {
        "start_event": start,
        "end_event": end,
        "activities": {node["id"]: node for node in nodes},
        "gateways": {},
        "flows": flows,
    }


def parallel_pipeline(first_node, second_node):
    first = deepcopy(first_node)
    second = deepcopy(second_node)
    gateway = {
        "id": "parallel",
        "name": "parallel",
        "type": "ParallelGateway",
        "incoming": "flow-start",
        "outgoing": ["flow-first", "flow-second"],
    }
    converge = {
        "id": "converge",
        "name": "converge",
        "type": "ConvergeGateway",
        "incoming": ["flow-first-converge", "flow-second-converge"],
        "outgoing": "flow-end",
    }
    first["incoming"] = "flow-first"
    first["outgoing"] = "flow-first-converge"
    second["incoming"] = "flow-second"
    second["outgoing"] = "flow-second-converge"

    return {
        "start_event": {"id": "start", "type": "EmptyStartEvent", "outgoing": "flow-start"},
        "end_event": {
            "id": "end",
            "type": "EmptyEndEvent",
            "incoming": "flow-converge-end",
            "outgoing": "",
        },
        "activities": {first["id"]: first, second["id"]: second},
        "gateways": {gateway["id"]: gateway, converge["id"]: converge},
        "flows": {
            "flow-start": {"id": "flow-start", "source": "start", "target": gateway["id"]},
            "flow-first": {"id": "flow-first", "source": gateway["id"], "target": first["id"]},
            "flow-second": {"id": "flow-second", "source": gateway["id"], "target": second["id"]},
            "flow-first-converge": {
                "id": "flow-first-converge",
                "source": first["id"],
                "target": converge["id"],
            },
            "flow-second-converge": {
                "id": "flow-second-converge",
                "source": second["id"],
                "target": converge["id"],
            },
            "flow-end": {"id": "flow-end", "source": converge["id"], "target": "end"},
        },
    }


def task_info(pipeline):
    return {"id": 1, "task_url": "/task/1", "pipeline_tree": pipeline}


def task_status(state, children):
    return {
        "state": state,
        "name": "task",
        "children": children,
        "elapsed_time": 1,
        "start_time": None,
        "finish_time": None,
    }


def test_unfolds_static_subprocess_when_runtime_children_are_empty(parse_sops_pipeline_tree):
    child_pipeline = linear_pipeline(service("child-1", "child 1"), service("child-2", "child 2"))
    pipeline = linear_pipeline(subprocess("sub", "subprocess", child_pipeline))
    status = task_status("RUNNING", {"sub": {"state": "RUNNING", "children": {}}})

    result = parse_sops_pipeline_tree(task_info(pipeline), status, is_parse_all=True)

    assert [step["step_name"] for step in result["step_data"]] == ["subprocess", "child 1", "child 2"]
    assert [step["step_status"] for step in result["step_data"]] == ["执行中", "未执行", "未执行"]
    assert result["total_step_num"] == 3


def test_unfolds_short_parallel_subprocess_when_runtime_children_are_empty(parse_sops_pipeline_tree):
    long_pipeline = linear_pipeline(service("long-child", "long child"))
    short_pipeline = linear_pipeline(
        service("short-child-1", "short child 1"), service("short-child-2", "short child 2")
    )
    pipeline = parallel_pipeline(
        subprocess("long", "long subprocess", long_pipeline),
        subprocess("short", "short subprocess", short_pipeline),
    )
    status = task_status(
        "RUNNING",
        {
            "long": {
                "state": "RUNNING",
                "children": {"long-child": {"state": "RUNNING", "children": {}}},
            },
            "short": {"state": "FINISHED", "children": {}},
        },
    )

    result = parse_sops_pipeline_tree(task_info(pipeline), status, is_parse_all=True)

    assert [step["step_name"] for step in result["step_data"]] == [
        "long subprocess",
        "long child",
        "short subprocess",
        "short child 1",
        "short child 2",
    ]
    assert result["total_step_num"] == 5


def test_empty_runtime_children_keep_five_step_window_safe(parse_sops_pipeline_tree):
    child_pipeline = linear_pipeline(
        service("child-1", "child 1"),
        service("child-2", "child 2"),
        service("child-3", "child 3"),
        service("child-4", "child 4"),
        service("child-5", "child 5"),
    )
    pipeline = linear_pipeline(subprocess("sub", "subprocess", child_pipeline))
    status = task_status("RUNNING", {"sub": {"state": "RUNNING", "children": {}}})

    result = parse_sops_pipeline_tree(task_info(pipeline), status, is_parse_all=False)

    assert [step["step_name"] for step in result["step_data"]] == ["subprocess", "child 1", "child 2"]
    assert len(result["step_data"]) <= 5


def test_successful_task_still_filters_nodes_without_runtime_status(parse_sops_pipeline_tree):
    pipeline = linear_pipeline(service("executed", "executed"), service("not-selected", "not selected"))
    status = task_status("FINISHED", {"executed": {"state": "FINISHED", "children": {}}})

    result = parse_sops_pipeline_tree(task_info(pipeline), status, is_parse_all=True)

    assert [step["step_name"] for step in result["step_data"]] == ["executed"]


@pytest.mark.parametrize(
    "state, expected_status",
    [
        ("SUSPENDED", "暂停"),
        ("NODE_SUSPENDED", "暂停"),
        ("REVOKED", "执行终止"),
    ],
)
def test_unfinished_special_states_generate_broadcast_result(
    parse_sops_pipeline_tree, state, expected_status
):
    pipeline = linear_pipeline(service("node", "node"))
    status = task_status(state, {"node": {"state": state, "children": {}}})

    result = parse_sops_pipeline_tree(task_info(pipeline), status, is_parse_all=False)

    assert result["task_status"] == expected_status
    assert result["current_step_num"] == 1
    assert result["step_data"][0]["step_status"] == expected_status
