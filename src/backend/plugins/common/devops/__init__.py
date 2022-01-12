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

from opsbot import on_command, CommandSession
from opsbot.log import logger
from component import DevOps
from .api import render_start_msg, parse_params, DevOpsTask
from .settings import (
    DEVOPS_PROJECT_TIP, DEVOPS_PIPELINE_TIP,
    DEVOPS_PIPELINE_START_SUCCESS, DEVOPS_PIPELINE_START_FAIL,
    SESSION_FINISHED_MSG,
    DEVOPS_PIPELINE_ALLOW_CMD, DEVOPS_PIPELINE_REFUSE_CMD, SESSION_FINISHED_CMD
)


@on_command('devops_project', aliases=('蓝盾流水线', '流水线', ))
async def list_project(session: CommandSession):
    user_id = session.ctx['msg_sender_id']
    projects = await DevOps().v3_app_project_list(user_id)
    rich_text = [{
        'type': 'link',
        'link': {
            'text': f'{item["projectName"]}, ',
            'type': 'click',
            'key': f'devops_pipeline_list|{user_id}|{item["projectCode"]}|{item["projectName"]}'
        }
    } for item in projects]
    rich_text.insert(0, {'text': {'content': DEVOPS_PROJECT_TIP}, 'type': 'text'})
    await session.send('', msgtype='rich_text', rich_text=rich_text)


@on_command('devops_pipeline_list', aliases=('devops_pipeline_list', ))
async def list_pipeline(session: CommandSession):
    _, user_id, project_id, project_name = session.ctx['event_key'].split('|')
    current_user_id = session.ctx['msg_sender_id']
    if user_id != current_user_id:
        return

    pipelines = await DevOps().v3_app_pipeline_list(project_id, user_id)
    rich_text = [{
        'type': 'link',
        'link': {
            'text': f'{item["pipelineName"]}, ',
            'type': 'click',
            'key': f'devops_pipeline_start|{user_id}|{project_id}|{item["pipelineId"]}|{item["pipelineName"]}'
        }
    } for item in pipelines.get('records', [])]
    rich_text.insert(0, {'text': {'content': f'{DEVOPS_PIPELINE_TIP} {project_name}\n'}, 'type': 'text'})
    await session.send('', msgtype='rich_text', rich_text=rich_text)


@on_command('devops_pipeline_start', aliases=('devops_pipeline_start', ))
async def devops_pipeline_start(session: CommandSession):
    if 'user_id' in session.state:
        user_id = session.state['user_id']
        project_id = session.state['project_id']
        pipeline_id = session.state['pipeline_id']
        pipeline_name = session.state['pipeline_name']
    else:
        _, user_id, project_id, pipeline_id, pipeline_name = session.ctx['event_key'].split('|')
        session.state['user_id'] = user_id
        session.state['project_id'] = project_id
        session.state['pipeline_id'] = pipeline_id
        session.state['pipeline_name'] = pipeline_name

    current_user_id = session.ctx['msg_sender_id']
    if user_id != current_user_id:
        return

    devops = DevOps()
    start_infos = await devops.v3_app_build_start_info(project_id, pipeline_id, user_id)
    params = await parse_params(start_infos, session)
    rich_text = render_start_msg(params, pipeline_name)
    reply, current_ctx = session.get('reply', prompt='...', msgtype='rich_text', rich_text=rich_text)
    while True:
        if reply == DEVOPS_PIPELINE_ALLOW_CMD:
            try:
                await devops.v3_app_build_start(project_id, pipeline_id, user_id, **params)
                msg = DEVOPS_PIPELINE_START_SUCCESS
            except Exception as e:
                msg = DEVOPS_PIPELINE_START_FAIL
                logger.error(f'{msg} {user_id} {project_id} {pipeline_id}, error: {e}')
                logger.exception(e)

            await session.send(msg)
            session.state.clear()
            break
        elif reply in [DEVOPS_PIPELINE_REFUSE_CMD, SESSION_FINISHED_CMD]:
            await session.send(SESSION_FINISHED_MSG)
            session.state.clear()
            break
        elif reply == 'devops_pipeline_params_commit':
            _, info_id = session.ctx['event_key'].split('|')
            reply = info_id
            session.state['reply'] = info_id
        else:
            del session.state['reply']
            info_value = session.get(reply, prompt=f'请输入参数 {reply}')
            session.state[reply] = info_value
            break


@on_command('bk_devops_project_list', aliases=('蓝盾流水线', 'bk_devops'))
async def _(session: CommandSession):
    try:
        bk_biz_id = session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
    except KeyError:
        bk_biz_id = None

    msg = await DevOpsTask(session, bk_biz_id).render_devops_project_list()
    msg and await session.send('', msgtype='template_card', template_card=msg)


@on_command('bk_devops_project_select')
async def _(session: CommandSession):
    msg = await DevOpsTask(session).render_devops_pipeline_list()
    msg and await session.send('', msgtype='template_card', template_card=msg)


@on_command('bk_devops_pipeline_select')
async def _(session: CommandSession):
    msg = await DevOpsTask(session).render_devops_pipeline_detail()
    msg and await session.send('', msgtype='template_card', template_card=msg)


@on_command('bk_devops_pipeline_update')
async def _(session: CommandSession):
    logger.info(session.ctx)


@on_command('bk_devops_pipeline_execute')
async def _(session: CommandSession):
    logger.info(session.ctx)


@on_command('bk_devops_pipeline_cancel')
async def _(session: CommandSession):
    _, bk_devops_pipeline_name = session.ctx['event_key'].split('|')
    content = f'''>**CI TIP** 
        ><font color=\"warning\">您的蓝盾流水线「{bk_devops_pipeline_name}」已取消...</font> 
        '''
    await session.send('', msgtype='markdown', markdown={'content': content})
