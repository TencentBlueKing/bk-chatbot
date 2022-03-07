# -*- coding: utf-8 -*-
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
import logging

from multiprocessing.pool import ThreadPool

logger = logging.getLogger("app")


def batch_request(func, params, get_data=lambda x: x["info"], get_count=lambda x: x["count"], limit=500):
    """
    并发请求接口
    :param func: 请求方法
    :param params: 请求参数
    :param get_data: 获取数据函数
    :param get_count: 获取总数函数
    :param limit: 一次请求数量
    :param app: 请求系统 ["cmdb"]
    :return: 请求结果
    """

    def generate_params(origin_params, _start, _limit):
        kwargs = json.loads(json.dumps(origin_params))
        kwargs["page"] = {"start": _start, "limit": _limit}
        return kwargs

    data = []
    start = 0

    # 请求第一次获取总数
    result = func(generate_params(params, start, 1))
    count = get_count(result)
    if count is None:
        return get_data(result)

    # 根据请求总数并发请求
    pool = ThreadPool()
    futures = []
    while start < count:
        futures.append(pool.apply_async(func, args=(generate_params(params, start, limit),)))
        start += limit

    pool.close()
    pool.join()

    # 取值
    for future in futures:
        data.extend(get_data(future.get()))

    return data
