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
import os

from django.conf import settings


def get_env_or_raise(key, default=None):
    """
    Get an environment variable, if it does not exist, raise an exception
    """
    value = os.environ.get(key, default)
    if not value and not hasattr(settings, "IS_TEST"):
        raise RuntimeError(
            ('Environment variable "{}" ' "not found, you must set this variable to run this application.").format(key),
        )
    return value
