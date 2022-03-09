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
import json
from os.path import dirname, abspath, join

MONGO_DB_HOST = os.getenv('MONGO_DB_HOST', '')
MONGO_DB_PORT = os.getenv('MONGO_DB_PORT', '')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', '')
MONGO_TABLE_NAME = os.getenv('MONGO_TABLE_NAME', '')
MONGO_DB_USERNAME = os.getenv('MONGO_DB_USERNAME', '')
MONGO_DB_PASSWORD = os.getenv('MONGO_DB_PASSWORD', '')

CUR_PATH = dirname(abspath(__file__))
BIZ_MODELS_DIR = join(CUR_PATH, 'biz_models')
STOP_WORDS_PATH = join(CUR_PATH, 'corpus', 'stopwords.txt')
SIMILAR_WORD_PATH = join(CUR_PATH, 'corpus', 'similar_word.json')
SIMILAR_WORD = json.load(open(SIMILAR_WORD_PATH))
# 是否启用从mongo获取语料，默认为False，启用为True
EXAMPLE_CORPUS_PATH = join(CUR_PATH, 'corpus', 'qa.json')
EXAMPLE_CORPUS = json.load(open(EXAMPLE_CORPUS_PATH))
# 是否触发训练，默认为False
NEED_TRAIN = False
USE_MONGO = False

SIMILAR_PERCENTAGE = 0.6
FILTER_PERCENTAGE = 0.75
