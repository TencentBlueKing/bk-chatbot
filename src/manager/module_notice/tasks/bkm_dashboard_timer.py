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
import time
import uuid
import base64
import logging

import requests
from celery.task import task

from src.manager.handler.api.bk_monitor import BkMonitor
from src.manager.handler.api.bk_chat import BkChat, check_wecom_group

logger = logging.getLogger("celery")


@task
def dashboard_send(payload):
    trace_id = str(uuid.uuid4())
    logger.info(f"[{trace_id}][dashboard_send] payload is {payload}")

    source = payload.get("source")
    sender = payload.get("sender")
    intent_name = payload.get("intent_name")
    try:
        panel_id = payload.get("panel_id")
        variables = payload.get("variables", {})

        # get sys variables value
        use_dashboard_default = variables.get("__sys__use_dashboard_default", "是") == "是"
        width = int(variables.get("__sys__width", 800))
        height = int(variables.get("__sys__height", 500))
        to_now_hours = int(variables.get("__sys__to_now_hours", 6))
        scale = int(variables.get("__sys__scale", 2))

        end_time = int(time.time())
        start_time = end_time - to_now_hours * 60 * 60
        options = {
            "bk_biz_id": int(payload.get("biz_id")),
            "dashboard_uid": payload.get("dashboard_uid"),
            "width": width,
            "start_time": start_time,
            "end_time": end_time,
            "scale": scale
        }
        if panel_id:
            options.update({
                "height": height,
                "panel_id": panel_id
            })

        if not use_dashboard_default:
            _variables = {k: v.split(",") for k, v in variables.items() if not k.startswith("__sys__") and v}
            options.update({
                "variables": _variables,
            })

        result = BkMonitor.start_render_image_task(options)
        task_id = result["task_id"]
        wait_time = 0
        while True:
            render_result = BkMonitor.get_render_image_task_result(task_id)

            if render_result.get("status", {}) == "success":
                image_url = render_result["image_url"]
                logger.info(f"[{trace_id}][dashboard_send] image render success, image url is {image_url}")
                break

            if render_result.get("status", {}) == "failed":
                raise Exception(f"[{trace_id}][dashboard_send] image render failed, error is {render_result['error']}")

            if wait_time >= 120:
                raise Exception(f"[{trace_id}][dashboard_send] image render timeout")

            time.sleep(1)
            wait_time += 2

        response = requests.get(image_url)
        response.raise_for_status()
        image_base64 = base64.b64encode(response.content).decode('utf-8')
        BkChat.file_send_service([source], image_url.split("?")[0].split("/")[-1], image_base64)

    except Exception as e:
        logger.exception(f"[{trace_id}][dashboard_send] error")
        error_msg = f"""<font color="#2151d1">{sender}</font>, 您的任务 [**{intent_name}**] <font color="#E53935">执行失败</font>
<font color="#858585"> TraceId</font>: {trace_id}
<font color="#858585"> 错误信息</font>: {str(e)}
"""
        kwargs = {
            "im": "WEWORK",
            "msg_type": "markdown",
            "msg_param": {"content": error_msg},
            "receiver": {
                "receiver_type": "group" if check_wecom_group(source) else "single",
                "receiver_ids": [source],
            },
            "headers": {},
        }
        BkChat.new_send_msg(**kwargs)
