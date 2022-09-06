# -*- coding: utf-8 -*-
import os

# SaaS应用ID
APP_CODE = os.environ.get("APP_ID", "")
# SaaS安全密钥，注意请勿泄露该密钥
SECRET_KEY = os.environ.get("APP_TOKEN", "")


def get_env_or_raise(key):
    """Get an environment variable, if it does not exist, raise an exception"""
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(
            ('Environment variable "{}" ' "not found, you must set this variable to run this application.").format(key),
        )
    return value


BKDATA_APIGW = get_env_or_raise("BKDATA_APIGW")  # 数据平台
BKDATA_URL = get_env_or_raise("BKDATA_URL")  # 数据平台
PAAS_API_HOST = get_env_or_raise("PAAS_API_HOST")  # 蓝鲸paas
PAAS_API_HOST_IEOD = get_env_or_raise("PAAS_API_HOST_IEOD")  # 蓝鲸paas
SOPS_APIGW = get_env_or_raise("SOPS_APIGW")  # 标准运维
BKMONITOR_APIGW = get_env_or_raise("BKMONITOR_APIGW")  # 蓝鲸监控
BK_ITSM_APIGW = get_env_or_raise("BK_ITSM_APIGW")  # 蓝鲸流程管理
BK_CHAT_APIGW = get_env_or_raise("BK_CHAT_APIGW")  # 蓝鲸信息流
BK_CHAT_NEW_APIGW = get_env_or_raise("BK_CHAT_NEW_APIGW")  # 蓝鲸信息流
LOG_SEARCH_APIGW = get_env_or_raise("LOG_SEARCH_APIGW")  # 日志平台
NODEMAN_APIGW = get_env_or_raise("NODEMAN_APIGW")  # 节点管理
DEVOPS_APIGW = get_env_or_raise("DEVOPS_APIGW")  # 蓝盾
MONITOR_URL = get_env_or_raise("MONITOR_URL")  # 蓝鲸监控
CSTONE_ESB_URL = get_env_or_raise("CSTONE_ESB_URL")  # 云石
