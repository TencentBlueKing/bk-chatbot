# -*- coding: utf-8 -*-
from django.conf import settings


def feature_switch(featue):
    # 如果未设置特性开关，则直接隐藏
    if featue not in settings.FEATURE_TOGGLE:
        return False

    # 灰度功能：非测试环境或管理员直接隐藏
    toggle = settings.FEATURE_TOGGLE[featue]
    if toggle == "off":
        return False
    elif toggle == "debug":
        if settings.ENVIRONMENT not in ["dev", "stag"]:
            return False

    return True
