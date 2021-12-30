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

from typing import Dict, List

from opsbot import CommandSession
from opsbot.command import kill_current_session
from .settings import SESSION_FINISHED_CMD, SESSION_FINISHED_MSG


def render_start_msg(params: Dict, pipeline_name: str):
    rich_text = [{'text': {'content': f'流水线: {pipeline_name}\r\n'}, 'type': 'text'}]
    for info_id, info_value in params.items():
        rich_text.extend([{
            'type': 'text',
            'text': {
                'content': f'{info_id}: {info_value}    '
            }
        }, {
            'type': 'link',
            'link': {
                'text': '修改\r\n',
                'type': 'click',
                'key': f'devops_pipeline_params_commit|{info_id}'
            }
        }])

    rich_text.append({'text': {'content': f'\r\n[是/否] 执行'}, 'type': 'text'})

    return rich_text


async def parse_params(start_infos: List, session: CommandSession):
    params = {}
    filter_infos = [info for info in start_infos.get('properties', []) if not info.get('propertyType')]
    for i, info in enumerate(filter_infos):
        if session.ctx['message'].extract_plain_text().find(session.bot.config.RTX_NAME) != -1:
            session.switch(param)

        if info['id'] in session.state:
            info["defaultValue"] = session.state[info['id']]

        prompt = f'请输入{info["id"]}'
        param = info["defaultValue"]
        if not info["defaultValue"]:
            param, ctx = session.get(info['id'], prompt=prompt)

        if param == SESSION_FINISHED_CMD:
            await session.send(SESSION_FINISHED_MSG)
            kill_current_session(session.ctx)
            return False

        params[info['id']] = param

    return params


