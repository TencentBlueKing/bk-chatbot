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


from blueapps.utils.logger import logger_celery as logger
from celery.task import task

from handler.api.bk_chat import BkChat
from module_timer.models import TimerModel


@task()
def callback(id: int):
    """
    回调机器人接口
    @param id:
    @return:
    """

    logger.info({"message": f"回调任务ID: {id}"})
    timer_obj = TimerModel.objects.get(pk=id)
    ret = BkChat.handle_scheduler(**timer_obj.exec_data)
    logger.info(ret)
