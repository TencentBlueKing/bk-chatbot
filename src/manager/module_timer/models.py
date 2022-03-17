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

from enum import Enum

from django.db import models
from django_filters import filters

from common.drf.filters import BaseOpenApiFilter
from common.models.base import BaseModel
from common.models.json import DictCharField


class TimerModel(BaseModel):
    """
    定时任务
    """

    class TimerType(Enum):
        DEFAULT = 0  # 默认值
        ONCE = 1  # 一次执行
        REPEAT = 2  # 重复执行

    class TimerStatus(Enum):
        OPEN = 1  # 启动状态
        CLOSE = 2  # 关闭状态

    biz_id = models.IntegerField("业务id")
    timer_name = models.CharField("定时任务名称", max_length=256)
    timer_type = models.IntegerField(
        "定时任务类型",
        default=TimerType.DEFAULT.value,
        choices=((tag.value, tag.name) for tag in TimerType),
    )
    timer_status = models.IntegerField(
        "定时任务状态",
        default=TimerStatus.OPEN.value,
        choices=((tag.value, tag.name) for tag in TimerStatus),
    )
    timer_user = models.CharField("定时任务添加人", default="", max_length=128)
    exec_data = DictCharField("执行数据")
    execute_time = models.CharField("一次执行时间", default="", max_length=256)
    expression = models.CharField("定时规则", default="", max_length=256)
    job_timer_id = models.IntegerField("job定时任务id", default=0)

    class Meta:
        db_table = "tab_timers"

    class OpenApiFilter(BaseOpenApiFilter):
        biz_id = filters.CharFilter(field_name="biz_id")
        timer_user = filters.CharFilter(field_name="timer_user")
        bk_app_code = filters.CharFilter(field_name="bk_app_code", method="self_ignore")
        bk_app_secret = filters.CharFilter(field_name="bk_app_secret", method="self_ignore")
