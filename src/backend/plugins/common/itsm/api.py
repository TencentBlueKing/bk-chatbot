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
from typing import Dict

from opsbot import CommandSession, IntentCommand
from opsbot.exceptions import ActionFailed, HttpFailed
from opsbot.log import logger
from component import RedisClient, ITSM, CC, Backend, BK_ITSM_DOMAIN
from component.config import BK_SUPER_USERNAME


class RuleParser:
    def __init__(self, session: CommandSession):
        self._session = session
        self._redis_client = RedisClient(env="prod")
        self.msg = self._session.ctx['message'].extract_plain_text()
        self.user_id = self._session.ctx["msg_sender_id"]
        self.biz_id = None
        self.receiver = None
        self.content = None

    class Conditions(object):
        def __init__(self, data: Dict, sender: str):
            self.data = data
            self.sender = sender

        def estimate(self):
            rule = 'COMMON_PLUGIN_ITSM_DAEMON'
            if self.sender == self.data.get('receiver'):
                rule = 'COMMON_PLUGIN_ITSM_SELF'

            return IntentCommand(100, rule, args=self.data)

    async def _pre(self):
        if self.msg.find("@") == -1:
            return None

        self.biz_id = self._redis_client.hash_get("chat_group_biz", self._session.ctx['msg_group_id'])
        if not self.biz_id or self.biz_id == '-1' or not self.biz_id.isdigit():
            return None

        try:
            if self.msg.startswith(f'@{self.user_id}') and not self.msg.startswith(f'@{self.user_id}('):
                self.content = self.msg[len(f'@{self.user_id}'):]
                self.receiver = self.user_id
            else:
                self.receiver = self.msg[self.msg.index("@") + 1: self.msg.index("(")]
                self.content = f'{self.msg[:self.msg.index("@")]}{self.msg[self.msg.index(")") + 1:]}'
        except ValueError:
            return None

        if not self.content:
            return None

        return {'biz_id': self.biz_id, 'receiver': self.receiver, 'content': self.content}

    async def evaluate(self):
        basic_info = await self._pre()
        if basic_info:
            return self.Conditions(basic_info, self.user_id).estimate()
        return None


class Ticket:
    def __init__(self, session: CommandSession):
        self._session = session
        self.user_id = self._session.ctx['msg_sender_id']
        self._redis_client = RedisClient(env="prod")

    def log(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except (HttpFailed, ActionFailed) as e:
                logger.error(f'{func.__name__} error: {args} {kwargs} {e}')
                self._session.send('提单失败')
            finally:
                # todo record click
                pass

        return wrapper

    async def is_exist(self, biz_id: str, group_id: str, sender: str, content: str) -> bool:
        data = self._redis_client.get(f'itsm_deamon:{biz_id}:{group_id}:{sender}:{content}')
        if data:
            await self._session.send(f'该单据已被{data.get("receiver")}处理')
            return True
        return False

    def _do_cache(self, biz_id: str, group_id: str, sender: str, content: str):
        self._redis_client.set(f'itsm_deamon:{biz_id}:{group_id}:{sender}:{content}',
                               json.dumps({"receiver": self.user_id}), ex=60 * 60 * 60, nx=True)

    @log
    async def refuse(self, biz_id: str, biz_name: str, content: str, group_id: str, sender: str):
        self._do_cache(biz_id, group_id, sender, content)
        await self._session.send(f'{biz_name} 单据已经被拒绝')

    @log
    async def create(self, biz_id: str, biz_name: str, content: str, group_id: str, sender: str):
        remark = f"{biz_name}_{content}"
        fields = [
            {"key": "urgency", "value": "2"},
            {"key": "start_time", "value": time.strftime("%Y-%m-%d")},
            {"key": "end_time", "value": time.strftime("%Y-%m-%d")},
            {"key": "bk_biz_id", "value": biz_id, "choice": [{"key": biz_id, "name": biz_name}]},
            {"key": "title", "value": remark[0:100]},
        ]

        response = await ITSM().create_ticket(creator=self.user_id, fields=fields, service_id=57)
        if response.get("sn", "") != "":
            if self.user_id != sender:
                self._do_cache(biz_id, group_id, sender, content)
                rich_text = [
                    {'type': 'text', 'text': {'content': f'{self.user_id}开始跟进处理, 需求内容：{content}'}},
                    {'type': 'mentioned', 'mentioned': {'userlist': [sender]}}
                ]
                await self._session.send('', msgtype='rich_text', rich_text=rich_text,
                                         receiver={'type': 'group', 'id': group_id})
            await self._session.send(f'【ITSM提单成功】\n单据ID：{response.get("sn", "")}\n网址：{BK_ITSM_DOMAIN}')

    async def send(self, biz_id: str, content: str, receiver: str):
        try:
            await Backend().get_opinion_type(text=content)
        except (ActionFailed, HttpFailed):
            return

        biz = await self.get_biz(bk_biz_id=int(biz_id), bk_biz_maintainer=receiver)
        if biz:
            biz_name = biz["bk_biz_name"]
            members = list(set("{},{}".format(biz["bk_biz_maintainer"], biz["bk_oper_plan"]).split(",")))
            msg_template = self.render_itsm_msg_template(biz_id, biz_name, self.user_id,
                                                         self._session.ctx['msg_group_id'], content)

            for member in members:
                await self._session.send('', msgtype='rich_text', rich_text=msg_template,
                                         receiver={'type': 'single', 'id': member})

    @classmethod
    async def get_biz(cls, **kwargs):
        response = await CC().search_business(bk_username=BK_SUPER_USERNAME, condition=kwargs)
        return response.get('info')[0] if response.get('count', 0) == 1 else None

    @classmethod
    def render_itsm_msg_template(cls, biz_id: str, biz_name: str, sender: str, group_id: str, content: str) -> Dict:
        return [
            {
                "text": {
                    "content": f"【ITSM需求处理单】\n\n业务： {biz_name}\n提单人：{sender}\n需求详情：{content}\n",
                },
                "type": "text"
            },
            {
                "type": "link",
                "link": {
                    "key": f"COMMON_PLUGIN_ITSM_DAEMON|create|{group_id}|{sender}|{biz_name}|{biz_id}|{content}",
                    "type": "click",
                    "text": "接受"
                }
            },
            {"text": {"content": "    "}, "type": "text"},
            {
                "type": "link",
                "link": {
                    "key": f"COMMON_PLUGIN_ITSM_DAEMON|refuse|{group_id}|{sender}|{biz_name}|{biz_id}|{content}",
                    "type": "click",
                    "text": "拒绝"
                }
            }
        ]


class GenericIT:
    def __init__(self, session: CommandSession):
        self._session = session
        self.user_id = self._session.ctx['msg_sender_id']
        self._itsm = ITSM()

    async def render_services(self):
        try:
            _, page = self._session.ctx['event_key'].split('|')
            page = int(page)
        except ValueError:
            return None

        services = await self._itsm.get_services()
        services = [{'id': str(var['id']), 'text': var['name']} for var in services]

        template_card = {
            'card_type': 'button_interaction',
            'source': {
                'desc': 'ITSM'
            },
            'main_title': {
                'title': '欢迎使用流程服务'
            },
            'task_id': str(int(time.time() * 100000)),
            'button_selection': {
                'question_key': 'bk_itsm_service_id',
                'title': '服务列表',
                'option_list': services[page:page+10]
            },
            'button_list': [
                {
                    "text": "提单",
                    "style": 1,
                    "key": "bk_itsm_select_service"
                },
                {
                    "text": "上页",
                    "style": 4,
                    "key": f"bk_itsm|{page - 10}"
                },
                {
                    "text": "下页",
                    "style": 4,
                    "key": f"bk_itsm|{page + 10}"
                }
            ]
        }
        return template_card

    async def render_service_detail(self):
        try:
            service_id = await self._session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
        except KeyError:
            return None

        service = self._itsm.get_service_detail(service_id=int(service_id))
        return {
            'card_type': 'text_notice',
            'source': {
                'desc': 'ITSM'
            },
            'main_title': {
                'title': f'已选择服务模版「{service["name"]}」点击填单'
            },
            'quote_area': {
                'quote_text': '\n'.join([field['name'] for field in service['fields']])
            },
            'task_id': str(int(time.time() * 100000)),
            'card_action': {
                'type': 1,
                'url': f'{BK_ITSM_DOMAIN}#/ticket/create?service_id={service_id}'
            }
        }