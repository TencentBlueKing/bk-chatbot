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

import time
import json
import base64

from typing import Dict, List

from opsbot import CommandSession
from component import BKCloud, RedisClient
from plugins.common.task.settings import (
    SESSION_APPROVE_REQ_MSG, SESSION_APPROVE_MSG
)


class Approval:
    session = None
    redis_client = None
    user_id = ''

    def __new__(cls, session: CommandSession):
        cls.session = session
        cls.user_id = session.ctx['msg_sender_id']
        cls.redis_client = RedisClient(env='prod')
        return cls

    @classmethod
    async def use_bk_itsm(cls, intent: Dict, slots: List, content: str):
        biz_id = intent.get('biz_id')
        intent_id = intent.get('id')
        key = f'opsbot_task:{cls.user_id}:{biz_id}:{intent_id}:{int(time.time())}'
        fields = [
            {'key': 'title', 'value': f'{intent.get("biz_id")}_BKCHAT任务审批'},
            {'key': 'content', 'value': content},
            {'key': 'approver', 'value': ','.join(intent['approver'])},
            {'key': 'id', 'value': base64.b64encode(bytes(key, encoding='utf-8')).decode('utf-8')},
        ]
        itsm = BKCloud().bk_service.itsm
        await itsm.create_ticket(creator=cls.user_id, fields=fields, service_id=116)
        cls.redis_client.set(f'{cls.session.bot.config.ID}:{key}', json.dumps({
            'intent': intent, 'slots': slots, 'user_id': cls.user_id,
            'group_id': cls.session.ctx['msg_group_id']
        }), ex=60 * 60 * 2)

    @classmethod
    def handle_approval_by_cache(cls, payload):
        key = base64.b64decode(payload.get('id')).decode('utf-8')
        return Approval.redis_client.get(f'{cls.session.bot.config.ID}:{key}')

    class BaseBot:
        @staticmethod
        def handle_approval(payload: Dict):
            return Approval.handle_approval_by_cache(payload)

        @staticmethod
        async def wait_approve(intent: Dict, slots: List):
            approver = intent.get('approver', [])
            if not approver:
                return False

            await Approval.session.send('提单中...')
            content = SESSION_APPROVE_REQ_MSG.format(Approval.user_id, intent["intent_name"],
                                                     '\n'.join([f"{slot['name']}：{slot['value']}" for slot in slots]))
            await Approval.use_bk_itsm(intent, slots, content)
            await Approval.session.send(SESSION_APPROVE_MSG.format(','.join(approver)))
            return True

    class Xwork(BaseBot):
        pass

    class Trigger(BaseBot):
        @staticmethod
        async def wait_approve(intent: Dict, slots: List):
            if not intent.get('approver', []):
                return False

            content = SESSION_APPROVE_REQ_MSG.format(Approval.user_id, intent["intent_name"],
                                                     '\n'.join([f"{slot['name']}：{slot['value']}" for slot in slots]))
            await Approval.use_bk_itsm(intent, slots, content)
            return True
