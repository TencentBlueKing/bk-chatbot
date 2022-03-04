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
from typing import Union, List, Dict

from opsbot import CommandSession
from opsbot.exceptions import ActionFailed, HttpFailed
from opsbot.log import logger
from opsbot.models import BKExecutionLog
from opsbot.plugins import GenericTask
from component import SOPS, RedisClient, BK_SOPS_DOMAIN, OrmClient


class SopsTask(GenericTask):
    def __init__(self, session: CommandSession, bk_biz_id: Union[str, int] = None):
        super().__init__(session, bk_biz_id, RedisClient(env='prod'))
        self._sops = SOPS()

    async def _get_sops_template_list(self, **params) -> List:
        data = await self._sops.get_template_list(self.biz_id, bk_username=self.user_id, **params)
        data.sort(key=lambda x: x['edit_time'], reverse=True)
        return [{'id': str(template['id']), 'text': template['name'], 'is_checked': False}
                for template in data[:20]]

    async def _get_sops_template_info(self, template_id: int) -> Dict:
        bk_sops_template_info = await self._sops.get_template_info(self.biz_id, template_id, bk_username=self.user_id)
        bk_sops_template_schemas = await self._sops.get_template_schemes(self.biz_id, template_id,
                                                                         bk_username=self.user_id)
        return {
            'bk_sops_template_info': bk_sops_template_info,
            'bk_sops_template_schemas': bk_sops_template_schemas
        }

    async def render_sops_template_list(self, **params):
        if not self.biz_id:
            return None

        bk_sops_templates = await self._get_sops_template_list(**params)
        return self._session.bot.send_template_msg('render_task_list_msg', 'SOPS', '欢迎使用标准运维', '请选择标准运维模板',
                                                   'bk_sops_template_id', bk_sops_templates, 'bk_sops_template_select')

    async def render_sops_template_info(self):
        if self._session.is_first_run:
            try:
                bk_sops_template_id = self._session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
            except (KeyError, TypeError):
                return None

            bk_sops_template = await self._get_sops_template_info(int(bk_sops_template_id))
            bk_sops_template_info = bk_sops_template['bk_sops_template_info']
            bk_sops_template_schemas = bk_sops_template['bk_sops_template_schemas']
            template_name = bk_sops_template_info['name']
            activities = [k for k, v in bk_sops_template_info.get('pipeline_tree', {}).get('activities').items()
                          if v['optional']]
            constants = [{'keyname': var['name'], 'value': var['value'] if var['value'] else '待输入'}
                         for var in bk_sops_template_info['pipeline_tree']['constants'].values()]
        else:
            bk_sops_template = self._session.state['bk_sops_template']
            bk_sops_template_id = bk_sops_template['bk_sops_template_id']
            template_name = bk_sops_template['bk_sops_template_name']
            bk_sops_template_schemas = bk_sops_template['bk_sops_template_schemas']
            activities = bk_sops_template['activities']
            constants = bk_sops_template['constants']

        info = {
            'bk_sops_template_id': bk_sops_template_id,
            'bk_sops_template_name': template_name,
            'bk_sops_template_schemas': bk_sops_template_schemas,
            'activities': activities,
            'constants': constants
        }

        template_card = {
            'card_type': 'button_interaction',
            'source': {
                'desc': 'SOPS'
            },
            'main_title': {
                'title': f'标准运维任务_{template_name}'
            },
            'task_id': str(int(time.time() * 100000)),
            'sub_title_text': '参数确认',
            'horizontal_content_list': constants,
            'button_list': [
                {
                    "text": "执行",
                    "style": 1,
                    "key": f"bk_sops_template_execute|{json.dumps(info)}"
                },
                {
                    "text": "修改",
                    "style": 2,
                    "key": f"bk_sops_template_update|{json.dumps(info)}"
                },
                {
                    "text": "取消",
                    "style": 3,
                    "key": f"bk_sops_template_cancel|{template_name}"
                },
                {
                    "text": "快捷键",
                    "style": 4,
                    "key": f"bk_shortcut_create|SOPS|{json.dumps(info)}"
                }
            ]
        }

        extra = {
            'button_selection': {
                'question_key': 'bk_sops_template_schema_id',
                'title': '分组',
                'option_list': [{'id': str(template['id']), 'text': template['name'], 'is_checked': False}
                                for template in bk_sops_template_schemas[:10]]
            }
        } if bk_sops_template_schemas else {}
        return self._session.bot.send_template_msg('render_task_select_msg', 'SOPS', f'标准运维任务_{template_name}',
                                                   constants, 'bk_sops_template_execute', 'bk_sops_template_update',
                                                   'bk_sops_template_cancel', info, template_name, **extra)

    async def execute_task(self, bk_sops_template: Dict) -> bool:
        if not bk_sops_template:
            return False

        bk_sops_template_id = bk_sops_template['bk_sops_template_id']
        bk_sops_template_name = bk_sops_template['bk_sops_template_name']
        bk_sops_template_schemas = bk_sops_template.get('bk_sops_template_schemas') or []
        activities = bk_sops_template['activities']
        constants = bk_sops_template['constants']

        try:
            bk_sops_template_schema_id = self._session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
            schema = {'data': item['data'] for item in bk_sops_template_schemas
                      if item['id'] == bk_sops_template_schema_id}
            select_group = json.loads(schema.get('data', []))
        except (KeyError, json.JSONDecodeError):
            select_group = None

        exclude_task_nodes_id = list(set(activities).difference(set(select_group))) if select_group else []
        constants = {constant['keyname']: constant['value'] for constant in constants}
        try:
            response = await self._sops.create_task(self.biz_id,
                                                    int(bk_sops_template_id),
                                                    name=bk_sops_template_name,
                                                    bk_username=self.user_id,
                                                    exclude_task_nodes_id=exclude_task_nodes_id,
                                                    constants=constants)
            await self._sops.start_task(self.biz_id, response.get('task_id'), bk_username=self.user_id)
            msg = f'{bk_sops_template_name} {constants} 任务启动成功'
            return True
        except ActionFailed as e:
            msg = f'{bk_sops_template_id} {constants} error: 参数有误 {e}'
        except HttpFailed as e:
            msg = f'{bk_sops_template_id} {constants} error: 第三方服务异常 {e}'
        finally:
            execution_log = BKExecutionLog(bk_biz_id=self.biz_id, bk_platform='SOPS', bk_username=self.user_id,
                                           feature_name=bk_sops_template_name, feature_id=str(bk_sops_template_id),
                                           detail=constants)
            OrmClient().add(execution_log)
            logger.info(msg)

        return False

    def render_sops_template_execute_msg(self, result: bool, bk_sops_template: Dict) -> Dict:
        return self.render_execute_msg('SOPS', result, bk_sops_template['bk_sops_template_name'],
                                       bk_sops_template['constants'], BK_SOPS_DOMAIN)
