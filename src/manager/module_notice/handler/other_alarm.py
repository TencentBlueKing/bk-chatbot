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
import json

from blueapps.utils.logger import logger
from common.design.my_asyncio import MyAsyncio
from src.manager.handler.api.bk_monitor import BkMonitor


class OtherPlatformAlarm:
    """
    1.通过策略ID和业务查询出对应的策略
    2.查询每个策略的处理套餐
        1).添加: 给策略新添处理套餐
        2).修改: 对策略进行初始化处理
        3).删除: 如果策略被去掉则直接删除
    """

    def __init__(self, biz_id, strategy_ids, config_id, new_strategy_ids):
        """
        @param biz_id:            业务ID
        @param strategy_ids:      策略ID列表
        @param config_id:
        @param del_strategy_ids:
        """
        self.biz_id = biz_id
        self.strategy_ids = strategy_ids
        self.new_strategy_ids = new_strategy_ids
        self.config_id = config_id
        self.action = self.get_action()

    def get_action(self):
        """
        @return:
        """
        action = {
            "config_id": self.config_id,
            "options": {
                "converge_config": {
                    "converge_func": "skip_when_success",
                    "timedelta": 60,
                    "count": 1,
                    "is_enabled": True,
                }
            },
            "signal": ["abnormal"],
        }
        return action

    def get_strategy_original_actions(self):
        """
        获取策略的原始套餐
        @return:
        """

        strategy_ids = list(map(lambda x: str(x), self.strategy_ids))
        params = {
            "page": 1,
            "page_size": 500,
            "conditions": [
                {
                    "key": "strategy_id",
                    "value": strategy_ids,
                }
            ],
            "bk_biz_id": self.biz_id,
        }
        # 获取告警策略详情
        result = BkMonitor.search_alarm_strategy_v3(**params)
        strategy_config_list = result.get("strategy_config_list")
        strategy_dict = {x.get("id"): x.get("actions") for x in strategy_config_list}
        return strategy_dict

    def update_single_strategy_action(self, strategy_id, actions):
        """
        更新单个告警处理套餐
        @param strategy_id:
        @param actions:
        @return:
        """
        params = {
            "ids": [strategy_id],
            "edit_data": {
                "actions": actions,
            },
            "bk_biz_id": self.biz_id,
        }
        result = BkMonitor.update_partial_strategy_v3(**params)
        return result

    async def _update_single_strategy_action(self, strategy_id, actions):
        """
        更新单个策略
        @param strategy_id:
        @param actions:
        @return:
        """

        return self.update_single_strategy_action(strategy_id, actions)

    def update_strategy_action(self):
        """
        更新策略的处理套餐
        @return:
        """
        strategy_dict = self.get_strategy_original_actions()

        tasks = []
        # 遍历更新策略
        for k, v in strategy_dict.items():
            actions = list(filter(lambda x: x.get("config_id") != self.config_id, v))
            # 删除策略
            if k in self.new_strategy_ids:
                actions.append(self.action)
            tasks.append(
                {
                    "func": self.update_single_strategy_action,
                    "args": (k, actions),
                }
            )

        # 如果tasks为空则无需进行处理
        if len(tasks) == 0:
            return
        # 利用协程并发处理
        with MyAsyncio() as go:
            data = go.async_run_until_complete(tasks)
        # 结果数据保存
        ret_list = MyAsyncio.get_task_result(data)
        # 日志记录
        logger.info({"message": f"更新策略结果:{json.dumps((ret_list))}"})
