import os
import requests

from blueapps.utils.logger import logger

AI_HOURS_REPORT_URL = os.getenv("AI_HOURS_REPORT_URL")
AI_HOURS_REPORT_TOKEN = os.getenv("AI_HOURS_REPORT_URL")


def report_task_data(task_data):
    headers = {
        'Report-Token': AI_HOURS_REPORT_TOKEN,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.request("POST", AI_HOURS_REPORT_URL, headers=headers, json=task_data)
        logger.info(f"Task[{task_data['task_uuid']}] report res is {response.text}")
    except Exception as e:
        logger.error(f"Task[{task_data['task_uuid']}] report error {str(e)}")
