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


class Regex(object):
    NUMBER = r"[0-9]+"
    ROLE_ID = r"[a-z_]+\.[a-z_]+"
    RESULT_TABLE_ID = r"\d+([_a-zA-Z0-9]+)"
    MODEL_ID = r"[_a-zA-Z0-9]+"

    # 没有约束，这里只限定不能为斜杠/
    EXCLUDE_SLASH = r"((?!\/).)*"
