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
import time
import traceback

from celery.task import task
from django.db import transaction

from blueapps.utils.logger import logger_celery as logger
from src.manager.handler.api.bk_itsm import BkITSM
from src.manager.module_plugin.hanlder.deal_plugin_status import deal_audit_plugin
from src.manager.module_plugin.models import PluginAuditLog


@task()
def update_status(sn: str):
    """
    更新日志定时任务
    """
    # 获取单据结果
    i, data = 0, []
    while i < 100:
        time.sleep(10)
        ret = BkITSM.ticket_approval_result(sn_list=[sn])
        logger.info({"message": json.dumps(ret)})
        result = ret.get("result", None)
        if not result:
            continue
        data = ret.get("data", [])
        current_status = data[0].get("approve_result")
        if current_status != "RUNNING":
            break
        i += 1

    if len(data) != 1:
        return
    # 审核结果
    approve_result = data[0].get("approve_result")
    try:
        with transaction.atomic():
            plugin_audit_log_obj = PluginAuditLog.objects.get(sn=sn)
            # 是否通过
            status = PluginAuditLog.SnStatus.PASS.value if approve_result else PluginAuditLog.SnStatus.NO_PASS.value
            # 插件审核
            deal_audit_plugin(plugin_audit_log_obj.plugin_id, approve_result)
            plugin_audit_log_obj.sn_status = status
            plugin_audit_log_obj.save()
    except ValueError:  # noqa
        # 日志记录
        logger.error(traceback.format_exc())
    except Exception:  # pylint: disable=broad-except
        # 日志记录
        logger.error(traceback.format_exc())
