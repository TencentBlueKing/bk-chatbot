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


#  * 时间表达式单元规范化对应的内部类,
#  * 对应时间表达式规范化的每个字段，
#  * 六个字段分别是：年-月-日-时-分-秒，
#  * 每个字段初始化为-1
class TimePoint:
    def __init__(self):
        self.tunit = [-1, -1, -1, -1, -1, -1]
