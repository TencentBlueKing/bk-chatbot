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

import datetime
import time


def mk_now_time(format="%Y-%m-%d %H:%M:%S"):
    """
    返回时间字符串
    """
    return time.strftime(format)


def mk_to_format_time(mk: int) -> str:
    """
    >>> mk_to_format_time(1625537379)
    '2021-07-06 10:09:39'

    """
    return datetime.datetime.strftime(datetime.datetime.fromtimestamp(mk), "%Y-%m-%d %H:%M:%S")


def mk_now_before_day(n: int) -> str:
    """
    获取多少天的日期
    @param n:
    @return:
    """
    before_day = datetime.datetime.now() - datetime.timedelta(days=n)
    return datetime.datetime.strftime(before_day, "%Y-%m-%d 00:00:00")


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
