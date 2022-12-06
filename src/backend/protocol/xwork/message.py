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

import re
import json
import time
from typing import Iterable, Tuple, Union, List, Dict, Optional

from opsbot.adapter import (
    Message as BaseMessage, MessageSegment as BaseMessageSegment,
    MessageTemplate as BaseMessageTemplate
)
from opsbot.stdlib import escape, unescape


TEMPLATE = {
    "text": {
        "Content": True
    },
    "Event": {
        "enter_chat": True,
        "click": True,
        "EventKey": True
    },
    "emotion": {
        "PicUrl": True
    },
    "image": {
        "PicUrl": True
    },
    "file": {
        "MediaId": True,
        "FileName": True
    },
    "voice": {
        "MediaId": True,
        "Format": True
    },
    "mixed": {
        "MixedMessage": True
    },
    "forward": {
        "ForwardMessage": True
    }
}


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

    @staticmethod
    def emotion(url: str):
        return MessageSegment(type_='emotion', data={'url': url})

    @staticmethod
    def file(_id: str):
        return MessageSegment(type_='file', data={'id': _id})

    @staticmethod
    def image(url: str):
        return MessageSegment(type_='image', data={'url': url})

    @staticmethod
    def voice(_id: int):
        return MessageSegment(type_='voice', data={'id': _id})

    @staticmethod
    def mixed(text: str):
        return MessageSegment(type_='mixed', data={'text': text})

    @staticmethod
    def forward(text: str):
        return MessageSegment(type_='forward', data={'text': text})

    @staticmethod
    def at(user_id: int):
        return MessageSegment(type_='at', data={'rtx': str(user_id)})


class Message(BaseMessage):
    @staticmethod
    def _normalized(msg_str: str) -> Iterable[MessageSegment]:
        def iter_function_name_and_extra() -> Iterable[Tuple[str, str]]:
            text_begin = 0
            for xwork_code in re.finditer(r'\[CQ:(?P<type>[a-zA-Z0-9-_.]+)'
                                          r'(?P<params>'
                                          r'(?:,[a-zA-Z0-9-_.]+=?[^,\]]*)*'
                                          r'),?\]',
                                          msg_str):
                yield 'text', unescape(
                    msg_str[text_begin:xwork_code.pos + xwork_code.start()])
                text_begin = xwork_code.pos + xwork_code.end()
                yield xwork_code.group('type'), xwork_code.group('params').lstrip(',')
            yield 'text', unescape(msg_str[text_begin:])

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
    def render_markdown_msg(cls, content: str) -> Dict:
        return {
            'msgtype': 'markdown',
            'markdown': {
                'content': content
            }
        }

    @classmethod
    def render_welcome_msg(cls, data: List, bk_biz_id: Union[int, str]) -> Dict:
        return {
            'msgtype': 'template_card',
            'template_card': {
                'card_type': 'button_interaction',
                'source': {
                    'desc': 'BKCHAT'
                },
                'main_title': {
                    'title': '欢迎使用蓝鲸信息流'
                },
                'task_id': str(int(time.time() * 100000)),
                'button_selection': {
                    'question_key': 'bk_biz_id',
                    'title': '业务',
                    'option_list': data[:10],
                    'selected_id': bk_biz_id if bk_biz_id else ''
                },
                'action_menu': {
                    'desc': '更多操作',
                    'action_list': [
                        {'text': '查找任务', 'key': 'bk_app_task_filter'},
                        {'text': '绑定业务', 'key': 'bk_cc_biz_bind'},
                        {'text': '快捷键', 'key': 'bk_shortcut_list'}
                    ]
                },
                'button_list': [
                    {
                        "text": "CI",
                        "style": 1,
                        "key": "bk_devops"
                    },
                    {
                        "text": "JOB",
                        "style": 1,
                        "key": "bk_job"
                    },
                    {
                        "text": "SOPS",
                        "style": 1,
                        "key": "bk_sops"
                    },
                    {
                        "text": "ITSM",
                        "style": 1,
                        "key": "bk_itsm|0"
                    }
                ]
            }
        }

    @classmethod
    def render_biz_list_msg(cls, data: List) -> Dict:
        return {
            'msgtype': 'template_card',
            'template_card': {
                'card_type': 'vote_interaction',
                'source': {
                    'desc': 'CC'
                },
                'main_title': {
                    'title': '欢迎使用配置平台',
                    'desc': '请选择业务'
                },
                'task_id': str(int(time.time() * 100000)),
                'checkbox': {
                    'question_key': 'bk_biz_id',
                    'option_list': data
                },
                'submit_button': {
                    'text': '提交',
                    'key': 'bk_cc_biz_select'
                }
            }
        }

    @classmethod
    def render_task_list_msg(cls, platform: str, title: str, desc: str, question_key: str,
                             data: List, submit_key: str, submit_text: str = '确认') -> Dict:
        if not data:
            return None

        return {
            'msgtype': 'template_card',
            'template_card': {
                'card_type': 'vote_interaction',
                'source': {
                    'desc': platform,
                    'desc_color': 1
                },
                'main_title': {
                    'title': title,
                    'desc': desc
                },
                'task_id': str(int(time.time() * 100000)),
                'checkbox': {
                    'question_key': question_key,
                    'option_list': data
                },
                'submit_button': {
                    'text': submit_text,
                    'key': submit_key
                }
            }
        }

    @classmethod
    def render_task_select_msg(cls, platform: str, title: str, params: List, execute_key: str,
                               update_key: str, cancel_key: str, data: Dict, task_name: str,
                               action=['执行', '修改', '取消', '快捷键'], **kwargs) -> Dict:
        button_map = {
            '执行': {
                "text": "执行",
                "style": 1,
                "key": f"{execute_key}|{json.dumps(data)}"
            },
            '修改': {
                "text": "修改",
                "style": 2,
                "key": f"{update_key}|{json.dumps(data)}"
            },
            '取消': {
                "text": "取消",
                "style": 3,
                "key": f"{cancel_key}|{task_name}"
            },
            '快捷键': {
                "text": "快捷键",
                "style": 4,
                "key": f"bk_shortcut_create|{platform}|{json.dumps(data)}"
            }
        }
        button_list = [v for k, v in button_map.items() if k in action]
        template = {
            'msgtype': 'template_card',
            'template_card': {
                'card_type': 'button_interaction',
                'source': {
                    'desc': platform,
                    'desc_color': 1
                },
                'main_title': {
                    'title': title
                },
                'task_id': str(int(time.time() * 100000)),
                'sub_title_text': '参数确认',
                'horizontal_content_list': params,
                'button_list': button_list
            }
        }
        template['template_card'].update(kwargs)
        return template

    @classmethod
    def render_task_execute_msg(cls, platform: str, task_name: str, task_result: bool,
                                params: List, task_domain: str) -> Dict:
        return {
            'msgtype': 'template_card',
            'template_card': {
                'card_type': 'text_notice',
                'source': {
                    'desc': platform
                },
                'main_title': {
                    'title': f'{task_name}启动成功' if task_result else f'{task_name}启动失败'
                },
                'horizontal_content_list': params,
                'task_id': str(int(time.time() * 100000)),
                'card_action': {
                    'type': 1,
                    'url': task_domain
                }
            }
        }

    @classmethod
    def render_task_filter_msg(cls, bk_app_task: Dict[str, List], bk_paas_domain: str):
        template = {
            'card_type': 'multiple_interaction',
            'source': {
                'desc': 'BKCHAT'
            },
            'main_title': {
                'title': '任务查询结果'
            },
            'task_id': str(int(time.time() * 100000))
        }

        if any(bk_app_task.values()):
            template['card_type'] = 'vote_interaction'
            template['submit_button'] = {'text': '确认', 'key': 'bk_app_task_select'}
            template['checkbox'] = {'question_key': 'bk_app_task_id', 'option_list': []}
        else:
            template['card_type'] = 'text_notice'
            template['main_title']['desc'] = '未找到对应任务'
            template['card_action'] = {'type': 1, 'url': bk_paas_domain}
            return template

        if bk_app_task['bk_job']:
            option_list = [
                {'id': f'bk_job|{str(job_plan["id"])}', 'text': f'JOB {job_plan["name"]}', 'is_checked': False}
                for job_plan in bk_app_task['bk_job'][:5]
            ]
            template['checkbox']['option_list'].extend(option_list)

        if bk_app_task['bk_sops']:
            option_list = [
                {'id': f'bk_sops|{str(template["id"])}', 'text': f'SOPS {template["name"]}', 'is_checked': False}
                for template in bk_app_task['bk_sops'][:5]
            ]
            template['checkbox']['option_list'].extend(option_list)

        return template


class MessageParser:
    @classmethod
    def parse_select(cls, ctx: Dict) -> Optional[str]:
        try:
            return ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
        except KeyError:
            return None

    @classmethod
    def parse_interaction(cls, ctx: Dict) -> Optional[Dict]:
        if 'event_key' in ctx:
            _, data = ctx['event_key'].split('|')
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return None

    @classmethod
    def update_select(cls, ctx: Dict, val: str):
        ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId'] = val
