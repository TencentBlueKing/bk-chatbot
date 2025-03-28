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

import os

import asyncio
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from opsbot.sched import Scheduler
from opsbot.log import logger
from component import BizMapper, Plugin, RedisClient

JOBS = [
    {
        "action": "refresh_corpus",
        "trigger": "interval",
        "interval": 60 * 60 * 1,
    },
    {
        "action": "reload_plugins",
        "trigger": "interval",
        "interval": 10,
    },
]


class Monitor:
    def __init__(self):
        self._scheduler = Scheduler(jobstores={"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")})
        self._loop = asyncio.get_event_loop()

    @classmethod
    async def reload_plugins(cls):
        redis_client = RedisClient(env="prod")
        plugin = Plugin(version="v2")
        data = await plugin.list()
        is_reload = False
        for item in data:
            node = await plugin.list(key=item["key"])
            md5 = redis_client.hash_get("plugins:md5", item["key"])
            if md5 and node and node.get("md5") == md5:
                continue

            logger.warn(f'LOAD PLUGIN: {node.get("name")} {md5} {node["md5"]}')
            is_reload = True
            try:
                redis_client.hash_set("plugins:md5", item["key"], node["md5"])
            except KeyError:
                logger.error(f"PLUGIN md5 missing: {node}")

        if is_reload:
            os.system("sh control restart")

    @classmethod
    async def refresh_corpus(cls):
        bm = BizMapper(top_rank=5)
        await bm.prepare_corpus()

    def deploy(self):
        for job in JOBS:
            self._scheduler.add_job(getattr(Monitor, job["action"]), "interval", seconds=job["interval"])

    def start(self):
        self._scheduler.start()
        try:
            self._loop.run_forever()
        except (KeyboardInterrupt, SystemExit):
            self._loop.stop()
            self._scheduler.shutdown()

    def run(self):
        self.deploy()
        self.start()


Monitor().run()
