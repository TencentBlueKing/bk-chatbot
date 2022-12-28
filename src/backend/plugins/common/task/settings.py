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

EXPR_DONT_UNDERSTAND = (
    _('无法理解你的意图...'),
    _('请确认是该群里的意图...')
)

EXPR_DONT_ALLOW = (
    _('你没有执行权限...'),
    _('请确认是否有该意图权限...'),
    _('请前往控制台确认权限...')
)

EXPR_DONT_ENABLE = (
    _('该技能未开启...'),
    _('请前往控制开修改该技能状态...'),
)

TASK_FILTER_KEY = 'bk_app_task_filter'
TASK_FILTER_ALIAS = (_('任务查找'), _('查找任务'))
TASK_FILTER_SELECT_KEY = 'bk_app_task_select'
TASK_LIST_KEY = 'bk_chat_task_list'
TASK_LIST_ALIAS = (_('自定义任务'), _('自定义技能'), _('技能'))
TASK_EXECUTE_KEY = 'bk_chat_task_execute'
TASK_CALLBACK_KEY = 'bk_chat_task_callback'
TASK_CALLBACK_ALIAS = ('handle_approval', 'handle_scheduler')
TASK_LIST_SCHEDULER_KEY = 'bk_chat_task_list_scheduler'
TASK_LIST_SCHEDULER_ALIAS = (_('查看定时任务'), _('查看定时'))
TASK_DEL_SCHEDULER_KEY = 'bk_chat_task_delete_scheduler'

TASK_SESSION_FINISHED_MSG = _('本次会话结束，您可以开启新的会话')
TASK_SESSION_FINISHED_CMD = _('结束')
TASK_SESSION_APPROVE_REQ_MSG = _('{}的技能「{}」执行权限申请，请您审批\n执行参数: {}')
TASK_SESSION_APPROVE_MSG = _('该技能已交由{}审批')
TASK_LIST_TIP = _('当前业务拥有的技能：\n')
TASK_FINISH_TIP = _('输入【结束】终止会话')
TASK_AUTHORITY_TIP = _('您没有权限点击')
TASK_ALLOW_CMD = _('是')
TASK_REFUSE_CMD = _('否')
TASK_EXEC_SUCCESS = _('任务启动成功')
TASK_EXEC_FAIL = _('任务启动失败')
TASK_EXEC_CANCEL = _('任务已取消')
TASK_FILTER_QUERY_PREFIX = _('请顺序输入任务名称')
TASK_FILTER_QUERY_TIP = _('支持模糊查询')
TASK_LIST_NULL_MSG = _('当前业务下无技能，请联系业务运维同学进行配置')
TASK_SKILL_SELECT_TIP = _('请选择BKCHAT自定义技能')
TASK_SKILL_RECOGNIZE_TIP = _('识别到技能：{}\r\n输入 [结束] 终止会话')
TASK_SKILL_SCHEDULER_TIP = _('识别到「定时」技能：{} 执行 {}\r\n输入 [结束] 终止会话')

PATTERN_IP = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}'
PATTERN_DYNAMIC_GROUP = '.*-.*-.*-.*-.*'

IS_USE_SQLITE = True
