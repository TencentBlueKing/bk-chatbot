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
