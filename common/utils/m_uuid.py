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

import random
import string
import uuid


def get_random_str(num=8):
    """
    获取随机数
    @param num:
    @return:
    """
    seed = string.digits + string.ascii_lowercase
    return "".join([random.choice(seed) for _ in range(num)])


def get_uuid4() -> str:
    """
    获取uuid字符串
    :return:
    """

    u = uuid.uuid4()
    return str(u)
