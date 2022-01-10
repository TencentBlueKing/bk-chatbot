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
from typing import Union, List

from opsbot import CommandSession
from opsbot.exceptions import ActionFailed, HttpFailed
from opsbot.log import logger
from opsbot.plugins import GenericTask
from component import SOPS, RedisClient, BK_SOPS_DOMAIN


class SopsTask(GenericTask):
    def __init__(self, session: CommandSession, bk_biz_id: Union[str, int] = None):
        self._redis_client = RedisClient(env='prod')
        super().__init__(session, bk_biz_id, self._redis_client)
        self._sops = SOPS()

    async def _get_sops_template_list(self, **params):
        data = await self._sops.get_template_list(self.biz_id, bk_username=self.user_id, **params)
        data.sort(key=lambda x: x['edit_time'], reverse=True)
        return [{'id': str(template['id']), 'text': template['name'], 'is_checked': False}
                for template in data[:20]]

    async def _get_sops_template_info(self, template_id: int):
        bk_sops_template_info = await self._sops.get_template_info(self.biz_id, template_id, bk_username=self.user_id)
        bk_sops_template_schemes = await self._sops.get_template_schemes(self.biz_id, template_id,
                                                                         bk_username=self.user_id)
        return {
            'bk_sops_template_info': bk_sops_template_info,
            'bk_sops_template_schemas': bk_sops_template_schemes
        }

    async def render_sops_template_list(self, **params):
        if not self.biz_id:
            return None

        bk_sops_templates = await self._get_sops_template_list(**params)
        template_card = {
            'card_type': 'vote_interaction',
            'source': {
                'desc': 'SOPS'
            },
            'main_title': {
                'title': '欢迎使用标准运维',
                'desc': '请选择标准运维模板'
            },
            'task_id': str(int(time.time() * 100000)),
            'checkbox': {
                'question_key': 'bk_sops_template_id',
                'option_list': bk_sops_templates
            },
            'submit_button': {
                'text': '确认',
                'key': 'bk_sops_template_select'
            }
        }
        return template_card

    async def render_sops_template_info(self):
        if self._session.is_first_run:
            try:
                bk_sops_template_id = self._session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
            except KeyError:
                return None

            bk_sops_template = await self._get_sops_template_info(int(bk_sops_template_id))
            self._redis_client.hash_set('plugins:bk_sops', self._session["TaskId"], bk_sops_template)
            bk_sops_template_schemas = bk_sops_template['bk_sops_template_schemes']

            template_name = bk_sops_template['name']
            constants = [{'keyname': var['name'], 'value': var['value'] if var['value'] else '待输入'}
                         for var in bk_sops_template['pipeline_tree']['constants'].values()]
        else:
            pass

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
                    "key": f"bk_sops_template_execute|{bk_sops_template_id}|{template_name}|{json.dumps(constants)}"
                },
                {
                    "text": "修改",
                    "style": 2,
                    "key": f"bk_sops_template_update|{bk_sops_template_id}|{template_name}|{json.dumps(constants)}"
                },
                {
                    "text": "取消",
                    "style": 3,
                    "key": f"bk_sops_template_cancel|{template_name}"
                }
            ]
        }

        if bk_sops_template_schemas:
            template_card['button_selection'] = {
                'question_key': 'bk_sops_template_schema_id',
                'title': '分组',
                'option_list': bk_sops_template_schemas
            }
        return template_card

    async def execute_task(self, bk_sops_template_id: Union[str, int], bk_sops_template_name: str, constants: List):
        bk_sops_template = self._redis_client.hash_get('plugins:bk_sops', self._session["TaskId"])
        if not bk_sops_template:
            return False

        bk_sops_template_info = bk_sops_template['bk_sops_template_info']
        bk_sops_template_schemas = bk_sops_template['bk_sops_template_schemas']
        activities = [k for k, v in bk_sops_template_info.get('pipeline_tree', {}).get('activities').items()
                      if v['optional']]

        try:
            bk_sops_template_schema_id = self._session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
            schema = {'data': item['data'] for item in bk_sops_template_schemas
                      if item['id'] == bk_sops_template_schema_id}
            select_group = schema.get('data', [])
        except KeyError:
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
            self._redis_client.hash_del('plugins:bk_sops', self._session["TaskId"])
            return True
        except ActionFailed as e:
            msg = f'{bk_sops_template_id} {constants} error: 参数有误 {e}'
        except HttpFailed as e:
            msg = f'{bk_sops_template_id} {constants} error: 第三方服务异常 {e}'
        finally:
            logger.info(msg)

        return False

    def render_sops_template_execute_msg(self, result: bool, bk_sops_template_name: str, constants: List):
        return self.render_execute_msg('SOPS', result, bk_sops_template_name, constants, BK_SOPS_DOMAIN)
