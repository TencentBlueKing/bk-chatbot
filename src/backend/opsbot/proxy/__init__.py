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
import functools
import logging
from typing import (
    Any, Dict, Union, List, AnyStr,
    Optional, Callable,
)

from quart import Quart, abort, jsonify

from opsbot.exceptions import *
from .bus import EventBus


def _deco_maker(post_type: str) -> Callable:
    def deco_deco(self, arg: Optional[Union[str, Callable]] = None, *events: str) -> Callable:
        def deco(func: Callable) -> Callable:
            if isinstance(arg, str):
                e = [post_type + '.' + e for e in [arg] + list(events)]
                self.on(*e)(func)
            else:
                self.on(post_type)(func)
            return func
        if isinstance(arg, Callable):
            return deco(arg)
        return deco
    return deco_deco


class Proxy(abc.ABC):
    def __init__(self,
                 secret: Optional[AnyStr] = None,
                 enable_http_post: bool = True,
                 message_class: type = None,
                 api_class: type = None,
                 *args, **kwargs):
        self._secret = secret
        self._bus = EventBus()
        self._server_app = Quart(__name__)

        self._server_app.route('/', methods=['GET'])(self._handle_url_verify)
        if enable_http_post:
            self._server_app.route('/', methods=['POST'])(self._handle_http)

        self._api = api_class
        self._message_class = message_class

    def __getattr__(self, item) -> Callable:
        return self._api.__getattr__(item)

    @property
    def asgi(self) -> Quart:
        return self._server_app

    @property
    def server_app(self) -> Quart:
        return self._server_app

    @property
    def logger(self) -> logging.Logger:
        return self._server_app.logger

    def subscribe(self, event: str, func: Callable) -> None:
        self._bus.subscribe(event, func)

    def unsubscribe(self, event: str, func: Callable) -> None:
        self._bus.unsubscribe(event, func)

    def on(self, *events: str) -> Callable:
        def deco(func: Callable) -> Callable:
            for event in events:
                self.subscribe(event, func)
            return func

        return deco

    @classmethod
    @abc.abstractmethod
    async def _handle_url_verify(cls):
        raise NotImplementedError

    @abc.abstractmethod
    async def _handle_http(self):
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, host=None, port=None, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    async def send(self, context: Dict[str, Any], message: Union[str, Dict[str, Any], List[Dict[str, Any]]], **kwargs):
        raise NotImplementedError


class Api:
    """
    API interface.
    """

    def __getattr__(self, item: str) -> Callable:
        """
        Get a callable that sends the actual API request internally.
        """
        return functools.partial(self.call_action, item)

    @abc.abstractmethod
    def _get_access_token(self, token_root: str) -> Any:
        pass

    @abc.abstractmethod
    def _handle_api_result(self, result: Optional[Dict[str, Any]]) -> Any:
        pass

    @abc.abstractmethod
    async def call_action(self, action: str, method='POST', **params) -> Optional[Dict[str, Any]]:
        """
        Send API request to call the specified action.
        """
        pass

    @abc.abstractmethod
    def _is_available(self) -> bool:
        pass


class UnifiedApi():
    """
    Call APIs through different communication methods
    depending on availability.
    """

    def __init__(self, *args,
                 http_api: Api = None,
                 ws_reverse_api: Api = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._http_api = http_api
        self._ws_reverse_api = ws_reverse_api

    async def call_action(self, action: str, **params) -> Any:
        result = None
        succeeded = False

        if self._ws_reverse_api:
            # WebSocket is preferred
            try:
                result = await self._ws_reverse_api.call_action(action, **params)
                succeeded = True
            except ApiNotAvailable:
                pass

        if not succeeded and self._http_api:
            try:
                result = await self._http_api.call_action(action, **params)
                succeeded = True
            except ApiNotAvailable:
                pass

        if not succeeded:
            raise ApiNotAvailable

        return result
