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

import sys
import types
from typing import Optional, Callable, Union, Coroutine

from .proxy.bus import EventBus
from .adapter import Bot
from .session import BaseSession
from .self_typing import Context_T
from .log import logger

_bus = EventBus()


def _make_event_deco(post_type: str) -> Callable:
    def deco_deco(arg: Optional[Union[str, Callable]] = None,
                  *events: str) -> Callable:
        def deco(func: Callable) -> Callable:
            if isinstance(arg, str):
                for e in [arg] + list(events):
                    _bus.subscribe(f'{post_type}.{e}', func)
            else:
                _bus.subscribe(post_type, func)
            return func

        if isinstance(arg, Callable):
            return deco(arg)
        return deco

    return deco_deco


def _log_event(ctx: Context_T) -> None:
    logger.info(f'Event: {ctx}')


class EventSession(BaseSession):
    __slots__ = ()

    def __init__(self, bot: Bot, ctx: Context_T):
        super().__init__(bot, ctx)


class EventHandler:
    """Universal, simple and effective syncronous event handler class, based in callbacks.

    Use as any classic event handler based in callbacks.

    eh = EventHandler('MyCoolEvent')
    eh.link(callback, 'MyCoolEvent')
    eh.fite('MyCoolEvent')

    Attributes:
        verbose (bool): Set True will output some messages, False will be silent.
        stream_output (IoStream): Set the stream to output messages.
        tolerate_exceptions (bool): Set True to ignore callbacks exceptions, False to raises it.
    """

    class Exceptions:
        """Custom error classes definition."""

        class EventNotAllowedError(Exception):
            """Will raise when tries to link a callback to unexistent event."""
            pass

    def __init__(self, *event_names, verbose=False, stream_output=sys.stdout, tolerate_callbacks_exceptions=False):
        """EventHandler initialization receives a list of allowed event names as arguments.

        Args:
            *event_names (str): Events names.
            verbose (bool): Set True to output warning messages.
            stream_output (IoStream): Set to send the output to specfic IO Stream object.
            tolerate_callbacks_exceptions (bool):
                False will raise any callback exception, stopping the execution.
                True will ignore any callbacks exceptions.
        """
        self.__events = {}
        self.verbose = verbose
        self.tolerate_exceptions = tolerate_callbacks_exceptions
        self.stream_output = stream_output

        if event_names:
            for event in event_names:
                self.register_event(str(event))  # cast as str to be safe

        logger.info(f'{self.__str__()} has been init.', file=self.stream_output) if self.verbose else None

    @property
    def events(self) -> dict:
        """Return events as dict."""
        return self.__events

    def clear_events(self) -> bool:
        """Clear all events."""
        self.__events = {}
        return True

    @property
    def event_list(self) -> [str]:
        """Return list of register events."""
        return self.__events.keys()

    @property
    def count_events(self) -> int:
        """Return number of registered events."""
        return len(self.event_list)

    def is_event_registered(self, event_name: str) -> bool:
        """Return if an event is current registered.

        Args:
            event_name (str): The event you want to consult.
        """
        return event_name in self.__events

    def register_event(self, event_name: str) -> bool:
        """Register an event name.

        Args:
            event_name (str): Event name as string.
        """
        if self.is_event_registered(event_name):
            logger.info(f'Omiting event {event_name} registration, already implemented',
                        file=self.stream_output) if self.verbose else None
            return False

        self.__events[event_name] = []
        return True

    def unregister_event(self, event_name: str) -> bool:
        """Unregister an event name.

        Args:
            event_name (str): Remove an event from events dict.
        """
        if event_name in self.__events:
            del self.__events[event_name]
            return True
        logger.info(f'Omiting unregister_event. {event_name} '
                    f'is not implemented.', file=self.stream_output) if self.verbose else None
        return False

    @staticmethod
    def is_callable(func: any) -> bool:
        """Return true if func is a callable variable.

        Args:
            func (callable): Object to validates as a callable.
        """
        return isinstance(func,
                          (types.FunctionType, types.BuiltinFunctionType, types.MethodType, types.BuiltinMethodType))

    def is_callback_in_event(self, event_name: str, callback: callable) -> bool:
        """Return if a given callback is already registered on the events dict.

        Args:
            event_name (str): The event name to look up for the callback inside.
            callback (callable): The callback function to check.
        """
        return callback in self.__events[event_name]

    def link(self, callback: callable, event_name: str) -> bool:
        """Link a callback to be executed on fired event..

        Args:
            callback (callable): function to link.
            event_name (str): The event that will trigger the callback execution.
        """

        if not self.is_callable(callback):
            logger.info(f'Callback not registered. Type {type(callback)} '
                        f'is not a callable function.', file=self.stream_output) if self.verbose else None
            return False

        if not self.is_event_registered(event_name):
            raise EventHandler.Exceptions.EventNotAllowedError(
                f'Can not link event {event_name}, not registered. Registered events are:'
                f' {", ".join(self.__events.keys())}. Please register event {event_name} before link callbacks.')

        if callback not in self.__events[event_name]:
            self.__events[event_name].append(callback)
            return True

        logger.info(f'Can not link callback {str(callback.__name__)}, already registered in '
                    f'{event_name} event.', file=self.stream_output) if self.verbose else None
        return False

    def unlink(self, callback: callable, event_name: str) -> bool:
        """Unlink a callback execution fro especific event.

        Args:
            callback (callable): function to link.
            event_name (str): The event that will trigger the callback execution.
        """
        if not self.is_event_registered(event_name):
            logger.info(f'Can not unlink event {event_name}, not registered. Registered events '
                        f'are: {", ".join(self.__events.keys())}. '
                        f'Please register event {event_name} before unlink callbacks.', file=self.stream_output)
            return False

        if callback in self.__events[event_name]:
            self.__events[event_name].remove(callback)
            return True

        logger.info(f'Can not unlink callback {str(callback.__name__)}, is not registered in '
                    f'{event_name} event.', file=self.stream_output) if self.verbose else None

        return False

    async def fire(self, event_name: str, *args, **kwargs) -> bool:
        """Triggers all callbacks executions linked to given event.

        Args:
            event_name (str): Event to trigger.
            *args: Arguments to be passed to callback functions execution.
            *kwargs: Keyword arguments to be passed to callback functions execution.
        """
        all_ok = True
        for callback in self.__events[event_name]:
            if not callable(callback):
                continue
            try:
                result = callback(*args, **kwargs)
                if isinstance(result, Coroutine):
                    await result
            except Exception as e:
                if not self.tolerate_exceptions:
                    raise e
                else:
                    if self.verbose:
                        logger.info(f'WARNING: {str(callback.__name__)} produces an exception error.',
                                    file=self.stream_output)
                        logger.info('Arguments', args, file=self.stream_output)
                        logger.info(e, file=self.stream_output)
                    all_ok = False
                    continue

        return all_ok

    def __str__(self) -> str:
        """Return a string representation."""

        mem_address = str(hex(id(self)))

        event_related = \
            [f"{event}:[{', '.join([callback.__name__ for callback in self.__events[event]])}]" for event in
             self.__events]

        return f'<class {self.__class__.__name__} at ' \
            f'{mem_address}: {", ".join(event_related)}, verbose={self.verbose}, ' \
            f'tolerate_exceptions={self.tolerate_exceptions}>'

    def __repr__(self) -> str:
        """Return python object representation."""
        return self.__str__()
