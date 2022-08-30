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

from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, wait

from common.constants import MAX_WORKER


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
