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

from os import path, getenv
from typing import List, Dict

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

import opsbot
try:
    import config as CONFIG
except ModuleNotFoundError:
    CONFIG = None

PRODUCT = getenv('PRODUCT', 'xwork')
PLUGINS = getenv('PLUGINS', 'common').split(',')


class Server:
    Base = declarative_base()

    def __init__(self, bot_name: str, plugins: List, config: Dict = None):
        self._bot_name = bot_name
        self._plugins = plugins
        self._config = config

    def init_db(self, url='sqlite:///tmp.db?check_same_thread=False'):
        engine = create_engine(url, echo=True)
        self.Base.metadata.create_all(engine, checkfirst=True)

    def run(self):
        self.init_db()
        opsbot.init(self._bot_name, self._config)
        for plugin in self._plugins:
            opsbot.load_plugins(path.join(path.dirname(__file__), 'plugins', plugin), f'plugins.{plugin}')
        opsbot.run()


Server(PRODUCT, PLUGINS, CONFIG).run()
