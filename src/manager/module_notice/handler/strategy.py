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

from common.design.strategy import Strategy
from src.manager.handler.api.bk_monitor import BkMonitor
from src.manager.module_notice.models import AlarmStrategyModel

BKM_STRATEGY_MAX_PAGE_SIZE = os.getenv("BKM_STRATEGY_MAX_PAGE_SIZE", 500)


class PlatformStrategy(Strategy):
    _map = dict()

    @classmethod
    def get(cls, platform: int, biz_id: int):
        """
        @param biz_id:
        @return:
        """
        return cls._map.value[platform](biz_id)


@PlatformStrategy.register(AlarmStrategyModel.AlarmSourceType.BCS.value)
def bcs():
    pass


@PlatformStrategy.register(AlarmStrategyModel.AlarmSourceType.BKM.value)
def bkm(biz_id):
    """
    bkm
    @param biz_id: 业务ID
    @return:
    """
    params = {
        "page": 1,
        "page_size": BKM_STRATEGY_MAX_PAGE_SIZE,
        "bk_biz_id": biz_id,
    }
    result = BkMonitor.search_alarm_strategy_v3(**params)
    strategy_config_list = result.get("strategy_config_list")
    # 查询策略ID和名称
    data = list(
        map(
            lambda x: {"id": x.get("id"), "name": x.get("name")},
            strategy_config_list,
        )
    )
    return data
