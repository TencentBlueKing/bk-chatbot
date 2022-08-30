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

import json
import uuid
import math

from blueapps.utils.logger import logger
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, wait

from common.constants import MAX_WORKER


def init_views(request):
    """
    初始化request参数
    :param request: 用户请求
    """
    req_data = {}
    try:
        req_data = json.loads(request.body)
    except Exception:  # pylint: disable=broad-except
        logger.error(
            f"[INIT_VIEWS] req_data parse error {request.body}",
        )

    ret_data = {
        "result": True,
        "data": [],
        "message": "",
        "request_id": str(uuid.uuid4()),
    }
    return req_data, ret_data


def get_request_user(request) -> str:
    """
    获取用户名称
    @param request:
    @return:
    """
    return request.user.username or request.COOKIES.get("bk_uid")


def get_request_biz_id(request) -> str:
    """
    返回biz_id
    @param request:
    @return:
    """
    logger.info(json.dumps({"cookies": request.COOKIES}))
    return request.COOKIES.get("biz_id")


def batch_request(
    func,
    params,
    get_data=lambda x: x["data"]["info"],
    get_count=lambda x: x["data"]["count"],
    page_size=500,
    page_param=lambda x, y: {"start": x, "length": y},
):
    """
    并发请求接口
    :param func: 请求方法
    :param params: 请求参数
    :param get_data: 获取数据函数
    :param get_count: 获取总数函数
    :param page_size: 一次请求最大数量
    :param page_param: 分页参数，默认使用start/limit分页，例如：{"cur_page_param":"start", "page_size_param":"limit"}
    :return: 请求结果
    """
    # 请求第一次获取总数
    result = func(**page_param(0, page_size), **params)

    if not result["result"]:
        message = f"batch request api {func} error,response {result}"
        logger.error(message)
        raise Exception(message)

    count = get_count(result)
    if count < page_size:
        return get_data(result)

    page = math.ceil(count / page_size)

    # 封装请求参数
    param_list = []
    for current_page in range(1, page + 1):
        param_list.append({**page_param(current_page, page_size), **params})

    max_workers = MAX_WORKER if len(param_list) > MAX_WORKER else len(param_list)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        task_list = [pool.submit(func, **param) for param in param_list]

    wait(task_list, return_when=ALL_COMPLETED)
    data = []
    for task in task_list:
        if not get_data(task.result()):
            message = f"batch request api {func} error,response {task.result()}"
            logger.exception()
            raise Exception(message)
        data += get_data(task.result())

    return data


def batch_exec_func(func_info_list):
    """
    批量请求不同接口的数据
    :param func_info_list: 不同请求方法的信息列表，例如:
        {
            "func": JOB().get_job_instance_list, # 方法
            "params": {}, # 方法对应参数
            "data_key": "", # batch_exec_func返回结果字典中该方法返回结果对应的key
        }
    """
    with ThreadPoolExecutor(max_workers=MAX_WORKER) as pool:
        task_list = [pool.submit(func_info["func"], **func_info["params"]) for func_info in func_info_list]

    wait(task_list, return_when=ALL_COMPLETED)

    data = {}
    for index, task in enumerate(task_list):
        data[func_info_list[index]["data_key"]] = task.result()

    return data
