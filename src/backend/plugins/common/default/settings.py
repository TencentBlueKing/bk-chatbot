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

from i18n import _

DEFAULT_INTENT_CATEGORY = os.getenv('DEFAULT_INTENT_CATEGORY', '').split(',')
DEFAULT_GUIDE_URL = os.getenv('DEFAULT_GUIDE_URL', '')
DEFAULT_HELPER = os.getenv('DEFAULT_HELPER', '').split(',')

DEFAULT_SHOW_GROUP_ID_ALIAS = (_('群ID'), _('群id'))
DEFAULT_BIND_BIZ_ALIAS = (
    _('绑定业务'), _('切换业务'), _('解绑业务'),
    _('业务绑定'), _('业务解绑'), _('业务切换')
)
DEFAULT_BIND_BIZ_TIP = _('查到你名下没有业务')
DEFAULT_QUERY_CHAT_KEY = 'bk_chat_group_id'
DEFAULT_WELCOME_KEY = 'bk_chat_welcome'
DEFAULT_BIND_ENV_KEY = 'bk_env_bind'
DEFAULT_BIND_BIZ_KEY = 'bk_cc_biz_bind'
DEFAULT_SELECT_BIZ_KEY = 'bk_cc_biz_select'
DEFAULT_SEARCH_QA_KEY = 'bk_chat_search_knowledge'
DEFAULT_HANDLE_CALLBACK_KEY = 'bk_chat_common_callback'

DEFAULT_SEARCH_QA_RESULT = _('结果')
DEFAULT_SEARCH_QA_QUESTION = _('问题')
DEFAULT_SEARCH_QA_ANSWER = _('答案')
