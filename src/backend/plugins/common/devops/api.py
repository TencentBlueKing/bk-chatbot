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
from typing import Union, Dict

from opsbot import CommandSession
from opsbot.plugins import GenericTask
from opsbot.log import logger
from opsbot.models import BKExecutionLog
from opsbot.exceptions import ActionFailed, HttpFailed
from component import DevOps, RedisClient, BK_DEVOPS_DOMAIN, OrmClient


class DevOpsTask(GenericTask):
    def __init__(self, session: CommandSession, bk_biz_id: Union[str, int] = None):
        super().__init__(session, bk_biz_id, RedisClient(env='prod'))
        self._devops = DevOps()

    async def _get_devops_project_list(self):
        data = await self._devops.v3_app_project_list(self.user_id)
        data.sort(key=lambda x: x['updatedAt'], reverse=True)
        return [{'id': str(project['projectCode']), 'text': project['projectName'], 'is_checked': False}
                for project in data[:20]]

    async def _get_devops_pipeline_list(self, project_id: str):
        data = (await self._devops.v3_app_pipeline_list(project_id, self.user_id)).get('records', [])
        data.sort(key=lambda x: x['latestBuildStartTime'], reverse=True)
        return [{'id': f'{project_id}|{project["pipelineId"]}|{project["pipelineName"]}',
                 'text': project['pipelineName'], 'is_checked': False} for project in data[:20]]

    async def _get_devops_build_start_info(self, project_id: str, pipeline_id: str):
        start_infos = await self._devops.v3_app_build_start_info(project_id, pipeline_id, self.user_id)
        filter_infos = [{'keyname': var['id'], 'value': var['defaultValue'] if var['defaultValue'] else '待输入'}
                        for var in start_infos.get('properties', []) if not var.get('propertyType')]
        return filter_infos

    async def render_devops_project_list(self):
        if not self.biz_id:
            return None

        bk_devops_projects = await self._get_devops_project_list()
        return self._session.bot.send_template_msg('render_task_list_msg', 'CI', '欢迎使用蓝盾平台', '请选择蓝盾项目',
                                                   'bk_devops_project_id', bk_devops_projects,
                                                   'bk_devops_project_select')

    async def render_devops_pipeline_list(self):
        try:
            bk_devops_project_id = self._session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
        except KeyError:
            return None

        bk_devops_pipelines = await self._get_devops_pipeline_list(bk_devops_project_id)
        return self._session.bot.send_template_msg('render_task_list_msg', 'CI', '欢迎使用蓝盾平台',
                                                   f'请选择「{bk_devops_project_id}」下流水线', 'bk_devops_pipeline_id',
                                                   bk_devops_pipelines, 'bk_devops_pipeline_select')

    async def render_devops_pipeline_detail(self):
        if self._session.is_first_run:
            try:
                bk_devops_pipeline_info = self._session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
                bk_devops_project_id, bk_devops_pipeline_id, bk_devops_pipeline_name = \
                    bk_devops_pipeline_info.split('|')
            except (KeyError, ValueError):
                return None

            start_infos = await self._get_devops_build_start_info(bk_devops_project_id, bk_devops_pipeline_id)
        else:
            bk_devops_pipeline = self._session.state['bk_devops_pipeline']
            bk_devops_project_id = bk_devops_pipeline['bk_devops_project_id']
            bk_devops_pipeline_id = bk_devops_pipeline['bk_devops_pipeline_id']
            bk_devops_pipeline_name = bk_devops_pipeline['bk_devops_pipeline_name']
            start_infos = bk_devops_pipeline['start_infos']

        info = {
            'bk_devops_project_id': bk_devops_project_id,
            'bk_devops_pipeline_id': bk_devops_pipeline_id,
            'bk_devops_pipeline_name': bk_devops_pipeline_name,
            'start_infos': start_infos
        }

        return self._session.bot.send_template_msg('render_task_select_msg', 'DevOps',
                                                   f'蓝盾流水线_{bk_devops_pipeline_name}', start_infos,
                                                   'bk_devops_pipeline_execute', 'bk_devops_pipeline_update',
                                                   'bk_shortcut_create', info, bk_devops_pipeline_name)

    async def execute_task(self, bk_devops_pipeline: Dict):
        bk_devops_project_id = bk_devops_pipeline['bk_devops_project_id']
        bk_devops_pipeline_id = bk_devops_pipeline['bk_devops_pipeline_id']
        bk_devops_pipeline_name = bk_devops_pipeline['bk_devops_pipeline_name']
        params = {item['keyname']: item['value'] for item in bk_devops_pipeline['start_infos']}

        try:
            await self._devops.v3_app_build_start(bk_devops_project_id, bk_devops_pipeline_id, self.user_id, **params)
            msg = f'{bk_devops_pipeline_name} {params} 任务启动成功'
            return True
        except ActionFailed as e:
            msg = f'{bk_devops_pipeline_id} {params} error: 参数有误 {e}'
        except HttpFailed as e:
            msg = f'{bk_devops_pipeline_id} {params} error: 第三方服务异常 {e}'
        finally:
            execution_log = BKExecutionLog(bk_biz_id=self.biz_id, bk_platform='DevOps', bk_username=self.user_id,
                                           feature_name=bk_devops_pipeline_name, feature_id=str(bk_devops_pipeline_id),
                                           project_id=bk_devops_project_id, detail=params)
            OrmClient().add(execution_log)
            logger.info(msg)

        return False

    def render_devops_execute_msg(self, result: bool, bk_devops_pipeline: Dict):
        return self.render_execute_msg('CI', result, bk_devops_pipeline['bk_devops_pipeline_name'],
                                       bk_devops_pipeline['start_infos'], BK_DEVOPS_DOMAIN)
