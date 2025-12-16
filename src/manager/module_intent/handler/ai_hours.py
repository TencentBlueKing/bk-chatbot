import os
import requests

from blueapps.utils.logger import logger_celery as logger

from common.models.base import to_format_date
from src.manager.module_intent.models import Intent

AI_HOURS_REPORT_URL = os.getenv("AI_HOURS_REPORT_URL")
AI_HOURS_REPORT_TOKEN = os.getenv("AI_HOURS_REPORT_TOKEN")


def report_task_data(task):
    headers = {
        'Report-Token': AI_HOURS_REPORT_TOKEN,
        'Content-Type': 'application/json'
    }
    task_uuid = task.task_uuid

    try:
        intent = Intent.objects.get(id=task.intent_id)
        task_data = {
            "task_uuid": task.task_uuid,
            "biz_id": task.biz_id,
            "intent_id": task.intent_id,
            "intent_name": task.intent_name,
            "intent_service_catalogue": intent.service_catalogue,
            "intent_create_user": task.intent_create_user,
            "sender": task.sender,
            "created_at": task.created_at,
            "updated_at": to_format_date(task.updated_at),
            "platform": task.platform,
            "task_id": task.task_id,
            "project_id": task.project_id,
            "feature_id": task.feature_id,
            "params": task.params,
            "status": task.status
        }
        logger.info(f"Task[{task_uuid}] report data is {task_data}")
        response = requests.request("POST", AI_HOURS_REPORT_URL, headers=headers, json=task_data)
        logger.info(f"Task[{task_uuid}] report res is {response.text}")
    except Exception as e:
        logger.error(f"Task[{task_uuid}] report error {str(e)}")
