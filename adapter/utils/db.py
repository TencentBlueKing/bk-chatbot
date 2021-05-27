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


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(list(zip(columns, row))) for row in cursor.fetchall()]


def array_group(data, key, group=0):
    if not data or len(data) == 0:
        return {}

    result = {}
    for item in data:
        if isinstance(item, dict):
            attr = item.get(key, None)
        else:
            attr = getattr(item, key, None)

        if attr is None:
            return {}

        if group != 0:
            if attr not in result:
                if isinstance(item, dict):
                    item["_nums"] = 1
                else:
                    item._nums = 1
            else:
                if isinstance(item, dict):
                    item["_nums"] = result[attr]["_nums"] + 1
                else:
                    item._nums = result[attr]._nums + 1

            result[attr] = item

        else:
            if attr not in result:
                result[attr] = []
            result[attr].append(item)
    return result


def array_hash(data, key, value):
    """
    获取一个DB对象的HASH结构
    """
    if not data or len(data) == 0:
        return {}

    result = {}
    for item in data:
        if isinstance(item, dict):
            attr = item.get(key, None)
        else:
            attr = getattr(item, key, None)

        if attr is None:
            return False

        if isinstance(item, dict):
            result[attr] = item.get(value, None)
        else:
            result[attr] = getattr(item, value, None)

    return result


def array_chunk(data, size=100):
    return [data[i : i + size] for i in range(0, len(data), size)]
