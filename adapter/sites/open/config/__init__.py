# -*- coding: utf-8 -*-
import os

# ==============================================================================
# 应用基本信息配置 (请按照说明修改)
# ==============================================================================
# 在蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 中获取 APP_ID 和 APP_TOKEN 的值
APP_CODE = os.environ.get("APP_ID", "")
SECRET_KEY = os.environ.get("APP_TOKEN", "")
BKAPP_DEVOPS_APIGW = os.getenv("BKAPP_DEVOPS_APIGW", "")  # 蓝盾host
SOPS_APIGW = os.getenv("SOPS_APIGW")  # 标准运维
BK_CHAT_APIGW = os.getenv("BK_CHAT_APIGW")  # bkchat
