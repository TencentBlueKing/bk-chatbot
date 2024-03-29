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
from typing import (
    Iterable, Tuple, Union, List, Dict, Optional,
    Callable
)

from opsbot.adapter import (
    Message as BaseMessage, MessageSegment as BaseMessageSegment,
    MessageTemplate as BaseMessageTemplate
)
from opsbot.stdlib import escape, unescape
from i18n import _


class MessageSegment(BaseMessageSegment):
    def __delitem__(self, key):
        pass

    def __str__(self):
        if self.is_text():
            return escape(self.data.get('text', ''), escape_comma=False)

        params = ','.join(('{}={}'.format(k, escape(str(v)))
                           for k, v in self.data.items()))
        if params:
            params = ',' + params
        return '[W:{type}{params}]'.format(type=self.type, params=params)

    def is_text(self) -> bool:
        return self.type == 'text'

    @staticmethod
    def text(text: str):
        return MessageSegment(type_='text', data={'text': text})


class Message(BaseMessage):
    @staticmethod
    def _normalized(msg_str: str) -> Iterable[MessageSegment]:
        def iter_function_name_and_extra() -> Iterable[Tuple[str, str]]:
            yield 'text', unescape(msg_str)

        for function_name, extra in iter_function_name_and_extra():
            if function_name == 'text':
                if extra:
                    # only yield non-empty text segment
                    yield MessageSegment(type_=function_name,
                                         data={'text': extra})
            else:
                data = {k: v for k, v in map(
                    lambda x: x.split('=', maxsplit=1),
                    filter(lambda x: x, (x.lstrip() for x in extra.split(',')))
                )}
                yield MessageSegment(type_=function_name, data=data)


class MessageTemplate(BaseMessageTemplate):
    @classmethod
    def render_markdown_msg(cls, title: str, content: str) -> Dict:
        def normalize(text: str) -> str:
            text = text.replace('<bold>', '*')
            text = text.replace('<warning>', '`')
            text = text.replace('<info>', '')
            return text

        # todo adapt more attribute
        return {
            "attachments": [
                {
                    "color": "#2eb886",
                    "title": normalize(title),
                    "title_link": "",
                    "text": normalize(content),
                    "footer": "bkchat",
                    "footer_icon": "",
                }
            ]
        }

    @classmethod
    def render_welcome_msg(cls, data: List, bk_biz_id: Union[int, str]) -> Dict:
        data = [
            {
                'value': str(biz['bk_biz_id']), 'text': biz['bk_biz_name']
            } for biz in data
        ]

        return {
            'text': '*BKCHAT*',
            'attachments': [
                {
                    'title': _('欢迎使用蓝鲸信息流'),
                    'callback_id': 'bk_chat_welcome|bk_cc_biz_select',
                    'color': '3AA3E3',
                    'attachment_type': 'default',
                    'actions': [
                        {
                            "name": "biz",
                            "text": _("请选择业务"),
                            "type": "select",
                            'selected_options': [
                                {
                                    'text': biz['text'],
                                    'value': biz['value']
                                } for biz in data if biz['value'] == str(bk_biz_id)
                            ][:1],
                            "options": data
                        }
                    ]
                },
                {
                    'text': _('请选择应用'),
                    'color': '3AA3E3',
                    'callback_id': 'bk_chat_welcome|bk_chat_app_select',
                    'actions': [
                        {
                            "name": "task",
                            "text": "CI",
                            "type": "button",
                            "value": "bk_devops"
                        },
                        {
                            "name": "task",
                            "text": "JOB",
                            "type": "button",
                            "value": "bk_job"
                        },
                        {
                            "name": "task",
                            "text": "SOPS",
                            "type": "button",
                            "value": "bk_sops"
                        },
                        {
                            "name": "task",
                            "text": "ITSM",
                            "type": "button",
                            "value": "bk_itsm"
                        }
                    ]
                }
            ]
        }

    @classmethod
    def render_biz_list_msg(cls, data: List):
        data = [
            {
                'value': str(biz['bk_biz_id']), 'text': biz['bk_biz_name']
            } for biz in data
        ]
        return {
            'text': '*BKCHAT*',
            'attachments': [
                {
                    'title': _('业务绑定'),
                    'callback_id': 'bk_cc_biz_select',
                    'color': '3AA3E3',
                    'attachment_type': 'default',
                    'actions': [
                        {
                            "name": "biz",
                            "text": _("请选择业务"),
                            "type": "select",
                            "options": data
                        }
                    ]
                }
            ]
        }

    @classmethod
    def render_task_list_msg(cls,
                             platform: str,
                             title: str,
                             desc: str,
                             question_key: str,
                             data: List,
                             submit_key: str,
                             submit_text: str = _('确认'),
                             render: Callable = None):
        if not data:
            return None

        if render:
            data = [render(x) for x in data]

        data = [
            {
                'value': str(task['id']), 'text': task['text']
            } for task in data
        ]

        return {
            'text': f'*{platform}*',
            'attachments': [
                {
                    'title': _(title),
                    'text': _(desc),
                    'callback_id': submit_key,
                    'color': '3AA3E3',
                    'attachment_type': 'default',
                    'actions': [
                        {
                            "action_id": question_key,
                            "name": "task",
                            "text": _("请选择实例"),
                            "type": "select",
                            "options": data
                        }
                    ]
                }
            ]
        }

    @classmethod
    def render_task_select_msg(cls,
                               platform: str,
                               title: str,
                               params: List,
                               execute_key: str,
                               update_key: str,
                               cancel_key: str,
                               data: Dict,
                               task_name: str,
                               action=[_('执行'), _('修改'), _('取消'), _('快捷键')],
                               **kwargs) -> Dict:
        if isinstance(data, dict):
            data.update({'platform': platform})

        button_list = [
            {
                "name": "operation",
                "text": _("执行"),
                "type": "button",
                "value": f"{execute_key}|{json.dumps(data)}",
                "confirm": {
                    "title": _("提示"),
                    "text": _("确认要执行该任务吗"),
                    "ok_text": _("是"),
                    "dismiss_text": _("否")
                }
            },
            {
                "name": "operation",
                "text": _("修改"),
                "type": "button",
                "value": f"{update_key}|{json.dumps(data)}"
            },
            {
                "name": "operation",
                "text": _("取消"),
                "type": "button",
                "value": f"{cancel_key}|{task_name}"
            },
            {
                "name": "operation",
                "text": _("快捷键"),
                "type": "button",
                "value": f"bk_shortcut_create|{json.dumps(data)}"
            }
        ]

        attachment_actions = [item for item in button_list if item['text'] in action]

        fields = [{
            'title': item['keyname'],
            'value': item['value'],
            'short': False
        } for item in params]

        return {
            'text': f'*{platform}*',
            'attachments': [
                {
                    'title': title,
                    'color': '3AA3E3'
                },
                {
                    'text': _('参数确认'),
                    'color': '3AA3E3',
                    'fields': fields
                },
                {
                    'text': '',
                    'callback_id': 'bk_chat_select_task|bk_task_action_select',
                    'color': '3AA3E3',
                    'attachment_type': 'default',
                    'actions': attachment_actions
                }
            ]
        }

    @classmethod
    def render_task_execute_msg(cls,
                                platform: str,
                                task_name: str,
                                task_result: bool,
                                params: List,
                                task_domain: str):
        fields = [{
            'title': item['keyname'],
            'value': item['value'],
            'short': False
        } for item in params]

        success_msg = _('启动成功')
        fail_msg = _('启动失败')
        return {
            'text': f'*{platform}*',
            'attachments': [
                {
                    'title':  _(f'{task_name}{success_msg}' if task_result else f'{task_name}{fail_msg}'),
                    'color': '3AA3E3'
                },
                {
                    'text': _('参数'),
                    'color': '3AA3E3',
                    'fields': fields
                }
            ]
        }

    @classmethod
    def render_task_filter_msg(cls, bk_app_task: Dict[str, List], bk_paas_domain: str):
        msg = {
            'text': '*BKCHAT*',
            'attachments': [
                {
                    'title': _('任务查询结果'),
                    'color': '3AA3E3'
                }
            ]
        }

        data = []
        if bk_app_task['bk_job']:
            data.extend([
                {'value': f'bk_job|{str(job_plan["id"])}', 'text': f'JOB {job_plan["name"]}'}
                for job_plan in bk_app_task['bk_job']
            ])

        if bk_app_task['bk_sops']:
            data.extend([
                {'value': f'bk_sops|{str(template["id"])}', 'text': f'SOPS {template["name"]}'}
                for template in bk_app_task['bk_sops']
            ])

        if any(bk_app_task.values()):
            msg['attachments'].append({
                'text': '',
                'callback_id': 'bk_app_task_filter|bk_app_task_select',
                'color': '3AA3E3',
                'attachment_type': 'default',
                'actions': [
                    {
                        "name": "task_filter_result_list",
                        "text": "",
                        "type": "select",
                        "options": data
                    }
                ]
            })
        else:
            msg['attachments'].append({
                'text': _('未找到对应任务'),
                'color': '3AA3E3',
                'actions': [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": _("平台")
                        },
                        "url": bk_paas_domain
                    }
                ]
            })

        return msg


class MessageParser:
    @classmethod
    def parse_select(cls, ctx: Dict) -> Optional[str]:
        try:
            for action in ctx['actions']:
                if action['type'] == 'select':
                    for select_action in action['selected_options']:
                        return select_action['value']
                elif action['type'] == 'button':
                    return action['value']
        except KeyError:
            return None

    @classmethod
    def parse_interaction(cls, ctx: Dict) -> Optional[Dict]:
        if 'callback_data' in ctx:
            data = ctx['callback_data']
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return None
