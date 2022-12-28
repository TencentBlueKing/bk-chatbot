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

from i18n import _
from plugins.common.job.api import JobTask
from plugins.common.sops.api import SopsTask
from plugins.common.devops import DevOpsTask


SHORTCUT_PROTO = {
    'JOB': JobTask,
    'SOPS': SopsTask,
    'CI': DevOpsTask
}

SHORTCUT_CREATE_KEY = 'bk_shortcut_create'
SHORTCUT_EXECUTE_KEY = 'bk_shortcut_execute'
SHORTCUT_LIST_KEY = 'bk_shortcut_list'
SHORTCUT_LIST_ALIAS = (_('查看快捷键'), _('快捷键'))
SHORTCUT_DELETE_KEY = 'bk_shortcut_delete'

SHORTCUT_WELCOME_TIP = _('欢迎使用快捷键服务')
SHORTCUT_COMMON_LABEL = _('快捷键')
SHORTCUT_NAME_INPUT_PREFIX = _('请输入快捷键名称')
SHORTCUT_NAME_FORMAT_TIP = _('最少输入8个字符, 每个人每个业务最多10个快捷键')
SHORTCUT_SAVE_TIP = _('保存成功')
SHORTCUT_DELETE_TIP = _('删除成功')
SHORTCUT_NULL_TIP = _('你还没有创建快捷键')
SHORTCUT_DELETE_TITLE = _('选择删除')
SHORTCUT_DELETE_SUBMIT_TEXT = _('删除')
