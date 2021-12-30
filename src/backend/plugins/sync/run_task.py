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

from typing import Dict
from collections import defaultdict

from jsonschema import validate as json_validate

from component import Backend
from component.public import Response
from plugins.common.task.api import real_run, Approval


schema_body = {
    "type": "object",
    "properties": {
        "serial": {"type": "string"},
        "slots": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": ["string", "number"]},
                    "name": {"type": "string"},
                    "value": {"type": "string"},
                    "type": {"type": ["string", "number"]}
                },
                "required": ["id", "value"],
                "extra_options": ["name"]
            }
        },
        "sender": {"type": "string"},
        "open_id": {"type": "string"}
    },
    "required": ["serial", "slots"],
    "extra_options": ["sender", "open_id"]
}


def validate(payload: Dict):
    json_validate(payload, schema_body)


async def run(payload: Dict) -> Dict:
    try:
        intent = (await Backend().describe('intents', serial_number=payload.get('serial')))[0]
    except IndexError:
        return Response(False, 40088, 'failed').__dict__

    slots = payload.get('slots')
    user_id = payload.get('sender') or 'trigger'
    group_id = payload.get('open_id')
    session = defaultdict(dict, ctx={'msg_sender_id': user_id, 'msg_group_id': group_id})

    is_approve = await getattr(Approval(session),
                               session.bot.type.title().replace('_', '')).wait_approve(intent, slots)
    if is_approve:
        return Response(msg='approving', data={'id': 000000}).__dict__

    data = await real_run(intent, slots, user_id, group_id)
    return Response('id' in data, 0 if 'id' in data else 40089, data.pop('msg', ''), data).__dict__
