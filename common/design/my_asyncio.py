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

    async def __make_async(self, func, *args):
        """
        生成异步任务
        @param func:
        @param args:
        @return:
        """
        loop = asyncio.get_event_loop()
        # 实际利用多线程异步解决
        future = loop.run_in_executor(None, func, *args)
        resp = await future
        return resp

    def async_run_until_complete(self, tasks):
        """
        把同步任务异步执行
        @param tasks:
        @return:
        """

        # 创建异步任务
        async_tasks = list(
            map(
                lambda x: self.__make_async(x.get("func"), *x.get("args")),
                tasks,
            )
        )

        # 异步执行任务
        data, _ = self.loop.run_until_complete(asyncio.wait(async_tasks))
        return data

    def run_until_complete(self, tasks):
        """
        直接执行异步任务
        @param tasks:
        @return:
        """
        # 异步执行任务
        data, _ = self.loop.run_until_complete(asyncio.wait(tasks))
        return data

    @classmethod
    def __get_single_result(self, ret):
        """
        获取单个处理结果
        @param ret:
        @return:
        """
        exception = ret.exception()
        if exception:
            return exception
        return ret.result()

    @classmethod
    def get_task_result(cls, data):
        """
        批量获取结果
        @param data:
        @return:
        """
        result_list = list(map(lambda x: cls.__get_single_result(x), data))
        return result_list

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
