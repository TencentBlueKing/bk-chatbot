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

import abc
import copy
from typing import List
from itertools import chain

from opsbot import CommandSession


class Action(abc.ABC):
    def __init__(self, key, index_msg, index_example, params_template, params_map):
        self.plugin_key = key
        self.plugin_index_msg = index_msg
        self.plugin_index_example = index_example
        self.plugin_params_template = params_template
        self.plugin_params_map = params_map

    def render_index_text(self, title='') -> List:
        if not title:
            title = f'{self.plugin_index_msg}{self.plugin_index_example}'
        rich_text = [{'text': {'content': title}, 'type': 'text'}]
        return rich_text

    def render_params_text(self, session: CommandSession) -> List:
        if not session.state.get('params'):
            session.state['params'] = copy.deepcopy(self.plugin_params_template)

        rich_text = [[{
            'type': 'text',
            'text': {
                'content': f'【{self.plugin_params_map[key]}】: {val}    '
            }
        }, {
            'type': 'link',
            'link': {
                'text': '修改\r\n',
                'type': 'click',
                'key': f'{self.plugin_key}.params|{key}'
            }
        }] for key, val in session.state.get('params').items()]

        return list(chain.from_iterable(rich_text))

    @classmethod
    def render_terminate_tip(cls) -> List:
        return [{'type': 'text', 'text': {'content': '(输入[结束]终止会话)'}}]

    def render_execute_text(self) -> List:
        return [{
            'type': 'link',
            'link': {
                'text': '执行     ',
                'type': 'click',
                'key': f'{self.plugin_key}.commit'
            }
        }, {
            'type': 'link',
            'link': {
                'text': '取消',
                'type': 'click',
                'key': f'{self.plugin_key}.cancel'
            }
        }]

    def switch_session(self, session: CommandSession):
        """
        exist plugin kill it
        """
        if session.ctx.get('event', '') == 'click' and session.ctx.get('event_key', '') != self.plugin_key:
            if session.ctx.get('event_key', '') in session.bot.config.SESSION_RESERVED_CMD:
                session.switch(session.ctx['message'])
                return True

        return False

    @abc.abstractmethod
    async def run(self, session: CommandSession):
        raise NotImplementedError
