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


import re


def camel_to_snake(name: str) -> str:
    """
    >>> camel_to_snake("FooBarBazQux")
    'foo_bar_baz_qux'
    >>> camel_to_snake("fooBarBazQux")
    'foo_bar_baz_qux'
    >>> camel_to_snake("aFooBarBazQux")
    'a_foo_bar_baz_qux'
    >>> camel_to_snake("FBI")
    'fbi'
    """
    name = re.sub("(.)([A-Z][a-z])+", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
