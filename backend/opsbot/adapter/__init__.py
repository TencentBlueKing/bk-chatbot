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
from typing import Any, Dict, Iterable

from opsbot.self_typing import Context_T


class Bot(abc.ABC):
    proxy: Any = None
    config: Dict = None

    @property
    @abc.abstractmethod
    def type(self) -> str:
        """
        Adapter type
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def type(self) -> str:
        """Adapter 类型"""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    async def check_permission(cls, ctx: Context_T, permission_required: int) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def handle_message(self, ctx: Context_T):
        raise NotImplementedError

    @abc.abstractmethod
    async def handle_event(self, ctx: Context_T):
        raise NotImplementedError

    @abc.abstractmethod
    async def call_api(self, action: str, **params):
        raise NotImplementedError


class MessageSegment(dict, abc.ABC):
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

    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError

    def __eq__(self, other):
        if not isinstance(other, MessageSegment):
            return False
        return self.type == other.type and self.data == other.data

    def __add__(self, other: Any):
        return Message(self).__add__(other)

    @abc.abstractmethod
    def is_text(self) -> bool:
        raise NotImplementedError


class Message(list, abc.ABC):
    def __init__(self, msg: Any = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(msg, (list, str)):
            self.extend(msg)
        elif isinstance(msg, dict):
            self.append(msg)

    @staticmethod
    @abc.abstractmethod
    def _normalized(msg_str: str) -> Iterable[MessageSegment]:
        raise NotImplementedError

    def __str__(self):
        return ''.join((str(seg) for seg in self))

    def __add__(self, other: Any):
        result = Message(self)
        if isinstance(other, Message):
            result.extend(other)
        elif isinstance(other, MessageSegment):
            result.append(other)
        elif isinstance(other, list):
            result.extend(map(lambda d: MessageSegment(d), other))
        elif isinstance(other, dict):
            result.append(MessageSegment(other))
        elif isinstance(other, str):
            result.extend(self._normalized(other))
        else:
            raise ValueError('the addend is not a valid message')

        return result

    def append(self, obj: Any) -> Any:
        if isinstance(obj, MessageSegment):
            super().append(obj)
        elif isinstance(obj, str):
            # self.extend(self._normalized(obj))
            self.append(MessageSegment(obj))
        else:
            raise ValueError('the object is not a valid message segment')

        return self

    def extend(self, msg: Any) -> Any:
        if isinstance(msg, str):
            msg = self._normalized(msg)

        for seg in msg:
            self.append(seg)

        return self

    def reduce(self) -> None:
        """
        Remove redundant segments.

        Since this class is implemented based on list,
        this method may require O(n) time.
        """
        idx = 0
        while idx < len(self):
            if idx > 0 and \
                    self[idx - 1].is_text() and self[idx].is_text():
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
            if seg.is_text():
                result += ' ' + seg.data['text']
        if result:
            result = result[1:]
        return result

