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

from enum import Enum
from functools import wraps
from typing import Callable


class Strategy(Enum):
    """
    策略注册
    """

    @classmethod
    def register(cls, key: int) -> Callable:
        """
        注册函数
        """

        def decorator(func):

            cls._map.value[key] = func

            @wraps(func)
            def wrapper(*args, **kwargs):
                func(*args, **kwargs)

            return wrapper

        return decorator
