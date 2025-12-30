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

from typing import Dict

from opsbot import CommandSession
from opsbot.plugins import GenericTool
from component import RedisClient


class Authority:
    """need meta"""
    def __init__(self, session: CommandSession):
        self._session = session
        self._redis_client = RedisClient(env='prod')
        self.bod_id = self._session.bot.config.ID
        self.bk_data = GenericTool.get_biz_data(self._session, self._redis_client)

    def pre_xwork(self) -> Dict:
        biz_id = self.bk_data.get('biz_id') if self.bk_data else -1
        return {
            'biz_id': int(biz_id),
            'available_user': [self._session.ctx['msg_sender_id']],
            'bk_env': self.bk_data.get('env')
        }

    def pre_slack(self) -> Dict:
        pass
