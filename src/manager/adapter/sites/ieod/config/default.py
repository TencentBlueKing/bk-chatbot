# -*- coding: utf-8 -*-
import os

# from config.default import FEATURE_TOGGLE

# pipeline 配置
# from pipeline.celery.settings import CELERY_QUEUES as PIPELINE_CELERY_QUEUES
# from pipeline.celery.settings import CELERY_ROUTES as PIPELINE_CELERY_ROUTES

RUN_VER_DISPLAY = os.environ.get("RUN_VER_DISPLAY", "内部版")
INIT_SUPERUSER = ["admin"]

CELERY_TIMEZONE = "Asia/Shanghai"

# celery路由配置
CELERY_ROUTES = {}
# CELERY_ROUTES.update(PIPELINE_CELERY_ROUTES)
# CELERY_QUEUES = PIPELINE_CELERY_QUEUES

# demo业务配置
BIZ_ACCESS_URL = os.getenv("BKAPP_BIZ_ACCESS_URL", "")
DEMO_BIZ_ID = os.getenv("BKAPP_DEMO_BIZ_ID", "")
DEMO_BIZ_EDIT_ENABLED = bool(os.getenv("BKAPP_DEMO_BIZ_EDIT_ENABLED", ""))
