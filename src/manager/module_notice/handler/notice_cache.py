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

from common.redis import RedisClient
from src.manager.module_notice.constants import NOTICE_GROUP_PREFIX
from src.manager.module_notice.models import (
    AlarmStrategyModel,
    NoticeGroupModel,
    TriggerModel,
)


def get_notice_group_data(notice_group_ids):
    """
    获取通知群组信息
    """
    notice_groups = NoticeGroupModel.objects.filter(id__in=notice_group_ids).values(
        "id",
        "name",
        "trigger_id",
        "biz_id",
        "group_type",
        "group_value",
    )
    notice_groups_data = []
    for notice_group in notice_groups:
        # 缓存数据获取
        with RedisClient() as r:
            notice_group_data = r.get(f"""{NOTICE_GROUP_PREFIX}_{notice_group.get("id")}""")
            if not notice_group_data:
                # 查询出对应的触发器然后调用
                t_id = notice_group.get("trigger_id")
                trigger_obj = TriggerModel.objects.get(id=t_id)
                notice_group_data = {
                    "notice_group": notice_group.get("id"),
                    "notice_group_name": notice_group.get("name"),
                    "im": trigger_obj.im_type_id,
                    "im_platform": trigger_obj.im_platform,
                    "headers": trigger_obj.info,
                    "receiver": {},
                    "biz_id": notice_group.get("biz_id"),
                }
                group_type = notice_group.get("group_type")
                receiver_ids = notice_group.get("group_value")
                if group_type and receiver_ids:
                    notice_group_data["receiver"] = {
                        "receiver_type": group_type,
                        "receiver_ids": receiver_ids,
                    }
                r.set(f"""{NOTICE_GROUP_PREFIX}_{notice_group.get("id")}""", json.dumps(notice_group_data), 60)
            else:
                notice_group_data = json.loads(notice_group_data)
            notice_groups_data.append(notice_group_data)
    return notice_groups_data


def get_notices(config_id):
    """
    根据策略获取通知群组
    @param config_id:
    @return:
    """
    alarm_strategy_obj = AlarmStrategyModel.objects.get(config_id=config_id)
    # 获取群组消息
    value = alarm_strategy_obj.deal_strategy_value
    notice_group_ids = value.get("notice_group_ids")
    return get_notice_group_data(notice_group_ids)


def get_config_info(config_id):
    """
    根据策略获取通知群组
    @param config_id:
    @return:
    """
    alarm_strategy_obj = AlarmStrategyModel.objects.get(config_id=config_id)
    # 获取群组消息
    value = alarm_strategy_obj.deal_strategy_value
    notice_group_ids = value.get("notice_group_ids")
    data = {
        "notice_groups": get_notice_group_data(notice_group_ids),
        "config_data": {
            "is_translated": alarm_strategy_obj.is_translated,
            "translation_type": alarm_strategy_obj.translation_type,
        },
    }
    return data
