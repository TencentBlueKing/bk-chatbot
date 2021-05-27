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
import asyncio
from collections import defaultdict
from typing import Callable, List, Any


class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(set)

    def subscribe(self, event: str, func: Callable) -> None:
        self._subscribers[event].add(func)

    def unsubscribe(self, event: str, func: Callable) -> None:
        if func in self._subscribers[event]:
            self._subscribers[event].remove(func)

    def on(self, event: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            self.subscribe(event, func)
            return func

        return decorator

    async def emit(self, event: str, *args, **kwargs) -> List[Any]:
        results = []
        while True:
            coros = []
            for f in self._subscribers[event]:
                coros.append(f(*args, **kwargs))
            if coros:
                results += await asyncio.gather(*coros)
            event, *sub_event = event.rsplit('.', maxsplit=1)
            if not sub_event:
                # todo adapt xwork
                # the current event is the root event
                break

        return results
