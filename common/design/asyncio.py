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


class MyAsyncio:
    def __init__(self, *args, **kwargs):
        """
        @param args:
        @param kwargs:
        """
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        self.loop = asyncio.get_event_loop()

    def run_until_complete(self, tasks):
        """
        执行任务
        @param tasks:
        @return:
        """
        data, _ = self.loop.run_until_complete(asyncio.wait(tasks))
        return data

    def __enter__(self):
        """
        @return:
        """
        return self

    def __exit__(self, *args, **kwargs):
        """
        @param args:
        @param kwargs:
        @return:
        """
        return self.loop.close()
