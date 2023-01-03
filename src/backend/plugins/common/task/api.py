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

import re
from collections import defaultdict
from typing import (
    Dict, List, Optional, Coroutine, Union, Tuple
)

from opsbot import CommandSession
from opsbot.helpers import render_expression
from opsbot.command import kill_current_session
from opsbot.log import logger
from opsbot.exceptions import ActionFailed, HttpFailed
from opsbot.plugins import GenericTask, GenericTool
from opsbot.models import BKExecutionLog
from component import (
    RedisClient, Cached, TimeNormalizer, OrmClient,
    IntentRecognition, BKCloud
)
from .settings import (
    TASK_SESSION_FINISHED_MSG, TASK_SESSION_FINISHED_CMD,
    TASK_ALLOW_CMD, TASK_REFUSE_CMD, TASK_EXEC_SUCCESS,
    TASK_EXEC_FAIL, PATTERN_IP, EXPR_DONT_ENABLE,
    IS_USE_SQLITE, TASK_SKILL_LABEL, TASK_EXECUTE_BUTTON,
    TASK_CANCEL_BUTTON, TASK_VALIDATE_PARAMS_MSG,
    TASK_CREATE_SCHEDULER_SUCCESS_PREFIX, TASK_URL_TIP,
    TASK_PARAMS_ERROR_TIP, TASK_API_ABNORMAL_TIP
)
from .apps import (
    Approval, Scheduler, CallbackHandler, Authority
)


class AppTask(GenericTask):
    def __init__(self, session: CommandSession, bk_biz_id: Union[str, int] = None, bk_env: str = 'v7'):
        super().__init__(session, bk_biz_id, RedisClient(env='prod'))
        self._bk_cloud = BKCloud(bk_env)
        self._backend = self._bk_cloud.bk_service.backend
        self._job = self._bk_cloud.bk_service.job
        self._sops = self._bk_cloud.bk_service.sops

    async def _get_app_task(self, task_name: str) -> Dict:
        bk_job_plans = await self._job.get_job_plan_list(bk_username=self.user_id, bk_biz_id=self.biz_id,
                                                         length=10, name=task_name)
        bk_sops_templates = await self._sops.get_template_list(self.biz_id, bk_username=self.user_id,
                                                               name_keyword=task_name)
        return {
            'bk_job': bk_job_plans.get('data', []),
            'bk_sops': bk_sops_templates,
            'bk_devops': []
        }

    async def render_app_task(self, task_name: str):
        bk_app_task = await self._get_app_task(task_name)
        return self._session.bot.send_template_msg('render_task_filter_msg',
                                                   bk_app_task,
                                                   self._bk_cloud.bk_service.BK_PAAS_DOMAIN)

    async def describe_entity(self, entity: str, **params):
        if 'biz_id' in params:
            params['biz_id'] = self.biz_id
        return await self._backend.describe(entity, **params)


class BKTask:
    """
    contain bk ci sops job platform
    intent -> task -> platform
    """
    def __init__(self,
                 intent: Dict,
                 slots: List,
                 user_id: str,
                 group_id: str = None,
                 bot_id: str = None,
                 bk_env: str = 'v7'):
        self._intent = intent
        self._slots = slots
        self._user_id = user_id
        self._group_id = group_id
        self._bot_id = bot_id or 'bkchat'
        self._executor = intent.get('updated_by') or user_id
        self._bk_cloud = BKCloud(bk_env)
        self.backend = self._bk_cloud.bk_service.backend

    async def run(self):
        tasks = await self.backend.describe('tasks', index_id=self._intent.get('id'))
        for task in tasks:
            result = await getattr(BKTask, f'_bk_{task.get("platform").lower()}')(self, task)
            try:
                log_id = await self._log(self._intent.get('biz_id'),
                                         result.get('platform'),
                                         result.get('task_id'),
                                         result.get('project_id', ''),
                                         result.get('project_id', 'pipeline_id'))
            except HttpFailed as e:
                logger.error(f'upload task log error: {str(e)}')
                log_id = -1
            result['id'] = log_id
            return result

    async def _log(self, biz_id, platform, task_id, project_id='', feature_id=''):
        if IS_USE_SQLITE:
            execution_log = BKExecutionLog(bk_biz_id=biz_id, bk_platform=platform, bk_username=self._user_id,
                                           feature_name=self._intent.get('intent_name'), feature_id=str(task_id),
                                           detail=self._slots)
            OrmClient().add(execution_log)
            return task_id
        else:
            return await self.backend.log(biz_id=biz_id, bot_type='default', bot_name=self._bot_id, msg='task',
                                          intent_id=self._intent.get('id'), intent_name=self._intent.get('intent_name'),
                                          platform=platform, task_id=task_id, sender=self._user_id,
                                          intent_create_user=self._executor, params=self._slots,
                                          project_id=project_id, feature_id=feature_id, rtx=self._group_id or '')

    async def _bk_job(self, task: Dict) -> Dict:
        # only allow string and host(ip)
        return await self._bk_cloud.bk_job(task, self._slots, self._intent.get('biz_id'),
                                           self._executor, _validate_pattern, PATTERN_IP)

    async def _bk_sops(self, task: Dict) -> Dict:
        return await self._bk_cloud.bk_sops(task, self._slots, self._intent.get('biz_id'), self._executor)

    async def _bk_devops(self, task: Dict) -> Dict:
        return await self._bk_cloud.bk_devops(task, self._slots, self._intent.get('biz_id'), self._executor)


def _validate_pattern(pattern, msg):
    result = re.findall(r'%s' % pattern, msg)
    return len(result) > 0


def summary_statement(intent: Dict, slots: List, other: str = '', is_click=False, session: CommandSession = None):
    intent_name = intent.get("intent_name")
    if is_click:
        params = [{'keyname': slot['name'], 'value': slot['value']} for slot in slots]
        statement = session.bot.send_template_msg('render_task_select_msg',
                                                  'BKCHAT',
                                                  f'{TASK_SKILL_LABEL}_{intent_name}',
                                                  params,
                                                  'bk_chat_task_commit',
                                                  'bk_chat_task_update',
                                                  'bk_chat_task_cancel',
                                                  intent,
                                                  intent_name,
                                                  [TASK_EXECUTE_BUTTON, TASK_CANCEL_BUTTON])
    else:
        params = '\n'.join([f"{slot['name']}：{slot['value']}" for slot in slots])
        statement = f'Task [{intent.get("intent_name")}] {other}\n{params}'

    return statement


async def parse_slots(slots: List, session: CommandSession):
    for slot in slots:
        if slot['value'] == '${USER_ID}':
            slot['value'] = session.ctx['msg_sender_id']
            continue

        if slot['value'] == '${GROUP_ID}':
            slot['value'] = session.ctx['msg_group_id']
            continue

        if slot['value']:
            continue

        param, ctx = session.get(slot['name'], prompt=slot['prompt'])
        if ctx['message'].extract_plain_text().find(session.bot.config.RTX_NAME) != -1:
            session.switch(param)

        if param == TASK_SESSION_FINISHED_CMD:
            await session.send(TASK_SESSION_FINISHED_MSG)
            kill_current_session(session.ctx)
            return False

        if _validate_pattern(slot['pattern'], param):
            slot['value'] = param
        else:
            await session.send(TASK_VALIDATE_PARAMS_MSG)
            return False

    return True


async def validate_intent(intents: List, session: CommandSession):
    """
    find most ratio intent and validate intent
    add some other nlp method
    """

    if not intents:
        return None
    intent = intents[0]
    if not intent.get('status'):
        await session.send(render_expression(EXPR_DONT_ENABLE))
        return None

    result = TimeNormalizer().parse(target=session.msg_text.strip())
    if 'error' not in result:
        intent['timer'] = result

    return intent


def wait_commit(intent: Dict, slots: List, session: CommandSession):
    """
    if config commit
    generate commit msg, wait user click
    """
    is_commit = 'bk_chat_task_execute'
    if intent.get('is_commit', True):
        prompt = summary_statement(intent, slots, '', True, session)
        while True:
            is_commit, ctx = session.get('is_commit', prompt='...', **prompt)
            if is_commit not in ['bk_chat_task_cancel', 'bk_chat_task_commit',
                                 TASK_ALLOW_CMD, TASK_REFUSE_CMD, TASK_SESSION_FINISHED_CMD]:
                del session.state['is_commit']
            else:
                break

    return is_commit in ['bk_chat_task_commit', TASK_ALLOW_CMD]


async def real_run(intent: Dict,
                   slots: List,
                   user_id: str,
                   group_id: str,
                   session: CommandSession = None,
                   bk_env: str = 'v7') -> Optional[Dict]:
    response = defaultdict(dict)
    try:
        if 'timer' in intent:
            timestamp = intent.pop('timer', {}).get('timestamp')
            exec_data = {'intent': intent, 'slots': slots, 'user_id': user_id, 'group_id': group_id}
            backend = BKCloud(bk_env).bk_service.backend
            await backend.set_timer(biz_id=intent.get('biz_id'), timer_name=intent.get('intent_name'),
                                    execute_time=timestamp, timer_status=1, timer_user=user_id,
                                    exec_data=exec_data, expression='')
            msg = f'{TASK_CREATE_SCHEDULER_SUCCESS_PREFIX}： {timestamp}'
        else:
            bot_id = session.bot.config.ID if session else None
            data = await BKTask(intent, slots, user_id, group_id, bot_id, bk_env).run()
            msg = summary_statement(intent, slots,
                                    f'{TASK_EXEC_SUCCESS}\r\n{TASK_URL_TIP}：{data.get("url")}',
                                    session=session)
            response.update(data)
    except ActionFailed as e:
        msg = f'{TASK_EXEC_FAIL} {intent.get("intent_name")}, error: {TASK_PARAMS_ERROR_TIP} {e}'
        logger.error(msg)
    except HttpFailed as e:
        msg = f'{TASK_EXEC_FAIL} {intent.get("intent_name")}, error: {TASK_API_ABNORMAL_TIP} {e}'
        logger.error(msg)
    finally:
        response['msg'] = msg

    return response


class Prediction:
    def __init__(self, session: CommandSession):
        self._session = session

    async def run(self, msg: str) -> Tuple:
        intent_filter = getattr(Authority(self._session), f'pre_{self._session.bot.type}')()
        if isinstance(intent_filter, Coroutine):
            intent_filter = await intent_filter
        if not intent_filter:
            return None

        bk_env = intent_filter.pop('bk_env', None)
        try:
            intents = await IntentRecognition(bk_env).fetch_intent(msg, **intent_filter)
        except ModuleNotFoundError:
            return None
        intent = await validate_intent(intents, self._session)
        if not intent:
            return None

        args = {
            'index': True,
            'intent': intent,
            'bk_env': bk_env,
            'slots': None,
            'user_id': self._session.ctx['msg_sender_id']
        }
        return intent.get('similar', 0) * 100, 'bk_chat_task_execute', args
