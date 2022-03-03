# -*- coding: utf-8 -*-


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
