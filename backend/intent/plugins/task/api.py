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
import json
import itertools
from typing import Dict, List

from opsbot import CommandSession
from opsbot.command import kill_current_session
from component import JOB, SOPS, Backend
from .settings import (
    SESSISON_FINISHED_MSG, SESSISON_FINISHED_CMD,
    TASK_ALLOW_CMD, TASK_REFUSE_CMD, PATTERN_IP
)


class BKTask:
    def __init__(self, intent: Dict, slots: List, user_id: str):
        self._intent = intent
        self._slots = slots
        self._user_id = user_id

    async def run(self):
        backend = Backend()
        tasks = await backend.describe('tasks', index_id=self._intent.get('intent_id'))
        for task in tasks:
            await getattr(BKTask, f'_bk_{task.get("platform").lower()}')(self, task)

    async def _bk_job(self, task: Dict):
        # only allow string and host(ip)
        global_var_list = [{
            'name': slot.get('name'), 'value': slot.get('value')
        } for slot in self._slots if slot.get('type') == 1]

        global_var_list.extend([{'id': slot.get('id'), 'server': {
            'ip_list': [{'bk_cloud_id': 0, 'ip': ip} for ip in slot['value'].split('\n')]
        }} for slot in self._slots if slot.get('type') == 3 and _validate_pattern(PATTERN_IP, slot.get('value'))])

        await JOB().execute_job_plan(
            bk_biz_id=self._intent.get('biz_id'),
            job_plan_id=int(task.get('task_id')),
            global_var_list=global_var_list,
            bk_username=self._user_id
        )

    async def _bk_sops(self, task: Dict):
        biz_id = self._intent.get('biz_id')
        user_id = self._user_id
        source = task.get('source', {})
        activities = [k
            for k, v in source.get('pipeline_tree', {}).get('activities').items()
            if v['optional']
        ]
        select_group = list(
            itertools.chain(*[json.loads(node['data']) for node in task.get('activities', [])])
        )
        exclude_task_nodes_id = list(
            set(activities).difference(set(select_group))
        ) if select_group else []
        constants = {slot['id']: slot['value'] for slot in self._slots}

        sops = SOPS()
        response = await sops.create_task(biz_id,
                                          task.get('task_id'),
                                          name=source.get('name'),
                                          bk_username=user_id,
                                          exclude_task_nodes_id=exclude_task_nodes_id,
                                          constants=constants)

        task_id = response.get('task_id')
        await sops.start_task(biz_id, task_id, bk_username=user_id)


def _validate_pattern(pattern, msg):
    result = re.findall(r'%s' % pattern, msg)
    return len(result) > 0


def summary_statement(intent: Dict, slots: List, other: str):
    params = '\r\n'.join([f"{slot['name']}：{slot['value']}" for slot in slots])
    statement = f"任务[{intent.get('intent_name')}] {other}"
    return f'{statement}\r\n{params}'


async def parse_slots(slots: List, session: CommandSession):
    for slot in slots:
        if slot['value']:
            continue

        param, ctx = session.get(slot['name'], prompt=slot['prompt'])
        if ctx['message'].extract_plain_text().find(session.bot.config.RTX_NAME) != -1:
            session.switch(param)

        if param == SESSISON_FINISHED_CMD:
            await session.send(SESSISON_FINISHED_MSG)
            kill_current_session(session.ctx)
            return False

        if _validate_pattern(slot['pattern'], param):
            slot['value'] = param
        else:
            await session.send('参数不合法，会话中断')
            return False

    return True


def wait_commit(intent: Dict, slots: List, session: CommandSession):
    is_commit = TASK_ALLOW_CMD
    if intent.get('is_commit', True):
        prompt = summary_statement(intent, slots, '可否执行，请输入 是/否')
        while True:
            is_commit, ctx = session.get('is_commit', prompt=prompt)
            if is_commit not in [TASK_ALLOW_CMD, TASK_REFUSE_CMD]:
                del session.state['is_commit']
            else:
                break

    return is_commit == TASK_ALLOW_CMD
