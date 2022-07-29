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

import os

CUR_PATH = os.path.dirname(os.path.abspath(__file__))
BASE_DICT_PATH = os.path.join(CUR_PATH, 'corpus', 'base_dict.txt')
STOP_WORDS_PATH = os.path.join(CUR_PATH, 'corpus', 'stopwords.txt')
BASE_CONFIDENCE = 0.6
ADVANCED_CONFIDENCE = 0.75

SIMILAR_WORD_LIB = {
    "状态": ["状态", "情况", "形态"],
    "增加": ["增加", "增长"],
    "安装": ["安装", "安置", "装置", "部署"],
    "日志": ["日志", "log"],
    "拉取": ["拉取", "获取"]
}
