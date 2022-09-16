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


def make_query(config: dict):
    """
    创建搜索条件

    :param config:
        查询配置
    """
    query = {}

    for k, v in config.items():
        if isinstance(v, (list, tuple)):
            # 时间条件
            if "__in" not in k and len(v) == 2:
                time_begin, time_end = v

                # 时间穷举
                if time_begin and not time_end:
                    query[k + "__gte"] = time_begin

                elif time_end and not time_begin:
                    query[k + "__lte"] = time_end

                elif time_begin and time_end:
                    if time_begin >= time_end:
                        raise Exception("began is greater than the end ")

                    query[k + "__gte"] = time_begin
                    query[k + "__lte"] = time_end

            # 集合条件
            else:
                query[k] = v

        else:
            # 字符条件
            if isinstance(v, str) and v:
                query[k] = v

            # 数值条件
            if isinstance(v, int):
                query[k] = v

            # 布尔条件
            if isinstance(v, bool):
                query[k] = v

    return query


def make_page(page: int, pagesize: int) -> (int, int):
    """
    通过
    @param page:
    @param pagesize:
    @return:
    """
    if not page or page < 1:
        return 0, 10**10
    start = (page - 1) * pagesize
    end = page * pagesize
    return start, end


def make_sql_query(config: dict):
    """
    生成原生sql的查询(暂时只支持全等查询)
    @param config:
    @return:
    """

    query_list = []
    for k, v in config.items():
        query_list.append(f"`{k}` = '{v}'")
    return "AND".join(query_list)
