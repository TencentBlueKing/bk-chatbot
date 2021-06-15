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

from collections import defaultdict

from opsbot import on_command, CommandSession
from opsbot.log import logger
from component import DevOps
from .api import parse_user_id
from .settings import (
    DEVOPS_PROJECT_TIP, DEVOPS_PIPELINE_TIP,
    DEVOPS_PIPELINE_START_SUCCESS, DEVOPS_PIPELINE_START_FAIL
)


@on_command('devops_project', aliases=('蓝盾流水线', ))
async def list_project(session: CommandSession):
    user_id = await parse_user_id(session)
    projects = await DevOps().v3_app_project_list(user_id)
    rich_text = [{
        'type': 'link',
        'link': {
            'text': f'{item["projectName"]}\n',
            'type': 'click',
            'key': f'devops_pipeline_list|{user_id}|{item["projectCode"]}'
        }
    } for item in projects]
    rich_text.insert(0, {'text': {'content': DEVOPS_PROJECT_TIP}, 'type': 'text'})
    await session.send('', msgtype='rich_text', rich_text=rich_text)


@on_command('devops_pipeline_list', aliases=('devops_pipeline_list', ))
async def list_pipeline(session: CommandSession):
    _, user_id, project_id = session.ctx['event_key'].split('|')
    pipelines = await DevOps().v3_app_pipeline_list(project_id, user_id)
    rich_text = [{
        'type': 'link',
        'link': {
            'text': f'{item["pipelineName"]}\n',
            'type': 'click',
            'key': f'devops_pipeline_start|{user_id}|{project_id}|{item["pipelineId"]}'
        }
    } for item in pipelines.get('records', [])]
    rich_text.insert(0, {'text': {'content': DEVOPS_PIPELINE_TIP}, 'type': 'text'})
    await session.send('', msgtype='rich_text', rich_text=rich_text)


@on_command('devops_pipeline_start', aliases=('devops_pipeline_start', ))
async def start_pipeline(session: CommandSession):
    if 'user_id' in session.state:
        user_id = session.state['user_id']
        project_id = session.state['project_id']
        pipeline_id = session.state['pipeline_id']
    else:
        _, user_id, project_id, pipeline_id = session.ctx['event_key'].split('|')
        session.state['user_id'] = user_id
        session.state['project_id'] = project_id
        session.state['pipeline_id'] = pipeline_id

    devops = DevOps()
    params = defaultdict(dict)
    start_infos = await devops.v3_app_build_start_info(project_id, pipeline_id, user_id)
    for info in start_infos.get('properties', []):
        if not info.get('propertyType'):
            param, ctx = session.get(info['id'], prompt=f'请输入{info["id"]}')
            params[info['id']] = param

    try:
        await devops.v3_app_build_start(project_id, pipeline_id, user_id, **params)
        msg = DEVOPS_PIPELINE_START_SUCCESS
    except Exception as e:
        msg = DEVOPS_PIPELINE_START_FAIL
        logger.error(f'{msg} {user_id} {project_id} {pipeline_id}, error: {e}')
        logger.exception(e)

    await session.send(msg)
    session.state.clear()
