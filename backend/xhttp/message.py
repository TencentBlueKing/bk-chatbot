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
from typing import Iterable, Dict, Tuple, Any


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


def escape(s: str, *, escape_comma: bool = True) -> str:
    s = s.replace('&', '&amp;') \
        .replace('[', '&#91;') \
        .replace(']', '&#93;')
    if escape_comma:
        s = s.replace(',', '&#44;')
    return s


def unescape(s: str) -> str:
    return s.replace('&#44;', ',') \
        .replace('&#91;', '[') \
        .replace('&#93;', ']') \
        .replace('&amp;', '&')


def _b2s(b: bool):
    if b:
        return 'true'
    else:
        return 'false'


class MessageSegment(dict):
    def __init__(self, d: Dict[str, Any] = None, *,
                 type_: str = None, data: Dict[str, str] = None):
        super().__init__()
        if isinstance(d, dict) and d.get('type'):
            self.update(d)
        elif type_:
            self['type'] = type_
            self['data'] = data or {}
        else:
            raise ValueError('the "type" field cannot be None or empty')

    def __getitem__(self, item):
        if item not in ('type', 'data'):
            raise KeyError(f'the key "{item}" is not allowed')
        return super().__getitem__(item)

    def __setitem__(self, key, value):
        if key not in ('type', 'data'):
            raise KeyError(f'the key "{key}" is not allowed')
        return super().__setitem__(key, value)

    def __delitem__(self, key):
        raise NotImplementedError

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            raise AttributeError(f'the attribute "{item}" is not allowed')

    def __setattr__(self, key, value):
        try:
            return self.__setitem__(key, value)
        except KeyError:
            raise AttributeError(f'the attribute "{key}" is not allowed')

    def __str__(self):
        if self.type == 'text':
            return escape(self.data.get('text', ''), escape_comma=False)

        params = ','.join(('{}={}'.format(k, escape(str(v)))
                           for k, v in self.data.items()))
        if params:
            params = ',' + params
        return '[W:{type}{params}]'.format(type=self.type, params=params)

    def __eq__(self, other):
        if not isinstance(other, MessageSegment):
            return False
        return self.type == other.type and self.data == other.data

    def __add__(self, other: Any):
        return Message(self).__add__(other)

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


class Message(list):
    def __init__(self, msg: Any = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if isinstance(msg, (list, str)):
                self.extend(msg)
            elif isinstance(msg, dict):
                self.append(msg)
            return
        except:
            pass
        raise ValueError('the msg argument is not recognizable')

    @staticmethod
    def _split_iter(msg_str: str) -> Iterable[MessageSegment]:
        """
        todo adapt xwork
        """
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

    def __str__(self):
        return ''.join((str(seg) for seg in self))

    def __add__(self, other: Any):
        result = Message(self)
        try:
            if isinstance(other, Message):
                result.extend(other)
            elif isinstance(other, MessageSegment):
                result.append(other)
            elif isinstance(other, list):
                result.extend(map(lambda d: MessageSegment(d), other))
            elif isinstance(other, dict):
                result.append(MessageSegment(other))
            elif isinstance(other, str):
                result.extend(Message._split_iter(other))
            return result
        except:
            pass
        raise ValueError('the addend is not a valid message')

    def append(self, obj: Any) -> Any:
        try:
            if isinstance(obj, MessageSegment):
                if self and self[-1].type == 'text' and obj.type == 'text':
                    self[-1].data['text'] += obj.data['text']
                elif obj.type != 'text' or obj.data['text'] or not self:
                    super().append(obj)
            else:
                self.append(MessageSegment(obj))
            return self
        except:
            pass
        raise ValueError('the object is not a valid message segment')

    def extend(self, msg: Any) -> Any:
        try:
            if isinstance(msg, str):
                msg = self._split_iter(msg)

            for seg in msg:
                self.append(seg)
            return self
        except:
            pass
        raise ValueError('the object is not a valid message')

    def reduce(self) -> None:
        """
        Remove redundant segments.

        Since this class is implemented based on list,
        this method may require O(n) time.
        """
        idx = 0
        while idx < len(self):
            if idx > 0 and \
                    self[idx - 1].type == 'text' and self[idx].type == 'text':
                self[idx - 1].data['text'] += self[idx].data['text']
                del self[idx]
            else:
                idx += 1

    def extract_plain_text(self, reduce: bool = False) -> str:
        """
        Extract text segments from the message, joined by single space.

        :param reduce: reduce the message before extracting
        :return: the joined string
        """
        if reduce:
            self.reduce()

        result = ''
        for seg in self:
            if seg.type == 'text':
                result += ' ' + seg.data['text']
        if result:
            result = result[1:]
        return result
