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

import json
import time
from typing import Union, Dict, List

from opsbot import CommandSession
from opsbot.command import kill_current_session
from opsbot.plugins import GenericTask
from component import DevOps, RedisClient
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


class DevOpsTask(GenericTask):
    def __init__(self, session: CommandSession, bk_biz_id: Union[str, int] = None):
        super().__init__(session, bk_biz_id, RedisClient(env='prod'))
        self._devops = DevOps()

    async def _get_devops_project_list(self):
        data = self._devops.v3_app_project_list(self.user_id)
        data.sort(key=lambda x: x['updatedAt'], reverse=True)
        return [{'id': str(project['projectCode']), 'text': project['projectName'], 'is_checked': False}
                for project in data[:20]]

    async def _get_devops_pipeline_list(self, project_id: str):
        data = self._devops.v3_app_pipeline_list(project_id, self.user_id)
        data.sort(key=lambda x: x['updateTime'], reverse=True)
        return [{'id': f'{project_id}|{project["pipelineId"]}|{project["pipelineName"]}',
                 'text': project['pipelineName'], 'is_checked': False} for project in data[:20]]

    async def _get_devops_build_start_info(self, project_id: str, pipeline_id: str):
        start_infos = self._devops.v3_app_build_start_info(project_id, pipeline_id, self.user_id)
        filter_infos = [{'keyname': var['id'], 'value': var['defaultValue'] if var['defaultValue'] else '待输入'}
                        for var in start_infos.get('properties', []) if not var.get('propertyType')]
        return filter_infos

    async def render_devops_project_list(self):
        if not self.biz_id:
            return None

        bk_devops_projects = await self._get_devops_project_list()
        template_card = {
            'card_type': 'vote_interaction',
            'source': {
                'desc': 'CI'
            },
            'main_title': {
                'title': '欢迎使用蓝盾平台',
                'desc': '请选择蓝盾项目'
            },
            'task_id': str(int(time.time() * 100000)),
            'checkbox': {
                'question_key': 'bk_devops_project_id',
                'option_list': bk_devops_projects
            },
            'submit_button': {
                'text': '确认',
                'key': 'bk_devops_project_select'
            }
        }
        return template_card

    async def render_devops_pipeline_list(self):
        try:
            bk_devops_project_id = self._session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
        except KeyError:
            return None

        bk_devops_pipelines = await self._get_devops_pipeline_list(bk_devops_project_id)
        template_card = {
            'card_type': 'vote_interaction',
            'source': {
                'desc': 'CI'
            },
            'main_title': {
                'title': '欢迎使用蓝盾平台',
                'desc': f'请选择「{bk_devops_project_id}」下流水线'
            },
            'task_id': str(int(time.time() * 100000)),
            'checkbox': {
                'question_key': 'bk_devops_pipeline_id',
                'option_list': bk_devops_pipelines
            },
            'submit_button': {
                'text': '确认',
                'key': 'bk_devops_pipeline_select'
            }
        }
        return template_card

    async def render_devops_pipeline_detail(self):
        if self._session.is_first_run:
            try:
                bk_devops_pipeline_info = self._session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
                bk_devops_project_id, bk_devops_pipeline_id, bk_devops_pipeline_name = \
                    bk_devops_pipeline_info.split('|')
            except (KeyError, ValueError):
                return None

            filter_infos = self._get_devops_build_start_info(bk_devops_project_id, bk_devops_pipeline_id)
        else:
            pass

        info = {
            'bk_devops_project_id': bk_devops_project_id,
            'bk_devops_pipeline_id': bk_devops_pipeline_id,
            'bk_devops_pipeline_name': bk_devops_pipeline_name,
            'params': filter_infos
        }

        template_card = {
            'card_type': 'button_interaction',
            'source': {
                'desc': 'CI'
            },
            'main_title': {
                'title': f'蓝盾流水线_{bk_devops_pipeline_name}'
            },
            'task_id': str(int(time.time() * 100000)),
            'sub_title_text': '参数确认',
            'horizontal_content_list': filter_infos,
            'button_list': [
                {
                    "text": "执行",
                    "style": 1,
                    "key": f"bk_devops_pipeline_execute|{json.dumps(info)}"
                },
                {
                    "text": "修改",
                    "style": 2,
                    "key": f"bk_devops_pipeline_update|{json.dumps(info)}"
                },
                {
                    "text": "取消",
                    "style": 3,
                    "key": f"bk_devops_pipeline_cancel|{bk_devops_pipeline_name}"
                }
            ]
        }
        return template_card
