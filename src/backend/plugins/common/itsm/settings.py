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

ITSM_KEY = 'bk_itsm'
ITSM_KEYWORDS = ('itsm提单', 'ITSM提单')

PLUGIN_KEY = 'bk_itsm'
PLUGIN_INDEX_MSG = '已选择: 创建itsm单据 \n'
PLUGIN_INDEX_EXAMPLE = 'eg: 创建itsm单据 服务 标题 正文\n'
PLUGIN_PARAMS_MAP = {
    'name': '单据标题',
    'catalog': '服务',
    'content': '正文',
}
PLUGIN_PARAMS_TEMPLATE = {
    'name': '',
    'catalog': '',
    'content': '',
}

PLUGIN_ACTION = 'bk_itsm.approve'
PLUGIN_KEYWORDS = {'itsm提单', '创建itsm单据'}
PLUGIN_FINISHED_CMD = '结束'
PLUGIN_FINISHED_MSG = '本次会话结束，您可以开启新的会话'
