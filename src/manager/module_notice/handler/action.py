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

from common.design.strategy import Strategy
from src.manager.handler.api.bk_monitor import BkMonitor
from src.manager.module_notice.models import AlarmStrategyModel


class Action(Strategy):
    @staticmethod
    def get_default_action(**kwargs):
        biz_id = kwargs.get("biz_id")
        name = kwargs.get("name")
        is_enabled = kwargs.get("is_enabled")
        # 从处理字段里面获取数据
        deal_strategy_value = kwargs.get("deal_strategy_value")
        url = deal_strategy_value.get("url")
        id = kwargs.get("config_id")
        notify_interval = kwargs.get("notify_interval", 1)  # 时间分钟
        my_content = {
            "callback_message": "{{alarm.callback_message}}",
            "config_id": "{{action.action_config_id}}",
        }
        params = {
            "execute_config": {
                "template_detail": {
                    "method": "POST",
                    "url": url,
                    "notify_interval": notify_interval * 60,  # 告警周期（按s为单位，最小1分钟，默认1h）
                    "failed_retry": {
                        "is_enabled": True,  # 是否启动
                        "max_retry_times": 2,
                        "retry_interval": 2,
                        "timeout": 10,
                    },
                    "authorize": {"auth_config": {}, "auth_type": "none", "insecure_skip_verify": False},
                    "body": {
                        "data_type": "raw",
                        "content_type": "json",
                        "content": json.dumps(my_content),
                        "params": [],
                    },
                },
                "timeout": 600,
            },
            "name": name,
            "desc": "通过bkchat管理端添加,如需删除，请移步到bkchat管理端进行删除",
            "bk_biz_id": biz_id,
            "plugin_id": 2,
            "is_enabled": is_enabled,
        }
        # 如果是update则需要添加id
        if id:
            params.setdefault("id", id)
        return params


class SaveAction(Strategy):
    _map = dict()

    @classmethod
    def save(cls, platform, **kwargs):
        """
        @param biz_id:
        @return:
        """
        return cls._map.value[platform](**kwargs)


class EditAction(Strategy):

    _map = dict()

    @classmethod
    def edit(cls, platform, **kwargs):
        """
        @param biz_id:
        @return:
        """
        return cls._map.value[platform](**kwargs)


class DelAction(Strategy):
    _map = dict()

    @classmethod
    def delete(cls, platform, **kwargs):
        """
        @param biz_id:
        @return:
        """
        return cls._map.value[platform](**kwargs)


@SaveAction.register(AlarmStrategyModel.AlarmSourceType.BCS.value)
def bcs_save():
    pass


@SaveAction.register(AlarmStrategyModel.AlarmSourceType.BKM.value)
def bkm_save(**kwargs):
    """
    bkm
    @param biz_id: 业务ID
    @return:
    """
    # 参数组合
    params = Action.get_default_action(**kwargs)
    result = BkMonitor.save_action_config(**params)
    config_id = result.get("id")
    return config_id


@EditAction.register(AlarmStrategyModel.AlarmSourceType.BCS.value)
def bcs_edit():
    pass


@EditAction.register(AlarmStrategyModel.AlarmSourceType.BKM.value)
def bkm_edit(**kwargs):
    """
    bkm
    @param biz_id: 业务ID
    @return:
    """
    params = Action.get_default_action(**kwargs)
    result = BkMonitor.edit_action_config(**params)
    config_id = result.get("id")
    return config_id


@DelAction.register(AlarmStrategyModel.AlarmSourceType.BCS.value)
def bcs_del():
    pass


@DelAction.register(AlarmStrategyModel.AlarmSourceType.BKM.value)
def bkm_del(**kwargs):
    """
    bkm
    @param biz_id: 业务ID
    @return:
    """
    config_id = kwargs.get("config_id")
    result = BkMonitor.delete_action_config(**{"id": config_id})
    return result
