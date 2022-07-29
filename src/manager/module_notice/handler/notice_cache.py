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
from src.manager.module_notice.models import (
    AlarmStrategyModel,
    NoticeGroupModel,
    TriggerModel,
)


def get_notices(config_id):
    """
    获取通知群组
    @param config_id:
    @return:
    """
    alarm_strategy_obj = AlarmStrategyModel.objects.get(config_id=config_id)
    # 获取群组消息
    value = alarm_strategy_obj.deal_strategy_value
    notice_group_ids = value.get("notice_group_ids")
    notice_groups = NoticeGroupModel.objects.filter(id__in=notice_group_ids).values(
        "id",
        "trigger_id",
        "biz_id",
        "group_type",
        "group_value",
    )
    notice_groups_data = []
    for notice_group in notice_groups:
        # 缓存数据获取
        with RedisClient() as r:
            notice_group_data = r.get(f"""notice_group_{notice_group.get("id")}""")
            if not notice_group_data:
                # 查询出对应的触发器然后调用
                t_id = notice_group.get("trigger_id")
                trigger_obj = TriggerModel.objects.get(id=t_id)
                notice_group_data = {
                    "notice_group": notice_group.get("id"),
                    "im": trigger_obj.im_type_id,
                    "headers": trigger_obj.info,
                    "receiver": {},
                }
                group_type = notice_group.get("group_type")
                receiver_ids = notice_group.get("group_value")
                if group_type and receiver_ids:
                    notice_group_data["receiver"] = {
                        "receiver_type": group_type,
                        "receiver_ids": receiver_ids,
                    }
                with RedisClient() as r:
                    r.set(f"""notice_group_{notice_group.get("id")}""", json.dumps(notice_group_data), 60)
            else:
                notice_group_data = json.loads(notice_group_data)
            notice_groups_data.append(notice_group_data)
    return notice_groups_data
