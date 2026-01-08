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
from typing import Iterable, Tuple

from opsbot.adapter import (
    Message as BaseMessage, MessageSegment as BaseMessageSegment,
)
from opsbot.stdlib import escape, unescape


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
        return '[WXAIBOT:{type}{params}]'.format(type=self.type, params=params)

    def is_text(self) -> bool:
        return self.type == 'text'

    @staticmethod
    def text(text: str):
        return MessageSegment(type_='text', data={'text': text})


class Message(BaseMessage):
    @staticmethod
    def _normalized(msg_str: str) -> Iterable[MessageSegment]:
        def iter_function_name_and_extra() -> Iterable[Tuple[str, str]]:
            text_begin = 0
            for code in re.finditer(r'\[WXAIBOT:(?P<type>[a-zA-Z0-9-_.]+)'
                                    r'(?P<params>'
                                    r'(?:,[a-zA-Z0-9-_.]+=?[^,\]]*)*'
                                    r'),?\]',
                                    msg_str):
                yield 'text', unescape(
                    msg_str[text_begin:code.pos + code.start()])
                text_begin = code.pos + code.end()
                yield code.group('type'), code.group('params').lstrip(',')
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
