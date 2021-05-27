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
REDIS_DB_PASSWORD = ''
REDIS_DB_PORT = 6379
REDIS_DB_NAME = ''

NLP_TOKEN = ''
NLP_ROOT = ''

EXPR_DONT_UNDERSTAND = (
    '无法理解你的意图...',
    '请确认是该群里的意图...'
)

SESSISON_FINISHED_MSG = '本次会话结束，您可以开启新的会话'
SESSISON_FINISHED_CMD = '结束'

TASK_ALLOW_CMD = '是'
TASK_REFUSE_CMD = '否'
TASK_EXEC_SUCCESS = '任务启动成功'
TASK_EXEC_FAIL = '任务启动失败'

PATTERN_IP = '^(?:[0-9]{1,3}\.){3}[0-9]{1,3}'
PATTERN_DYNAMIC_GROUP = '.*-.*-.*-.*-.*'
