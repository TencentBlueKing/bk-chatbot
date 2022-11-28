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
from common.constants import BKCHAT_CACHE_PREFIX

ALL_REQUEST_METHODS = ("GET", "POST", "HEAD", "OPTIONS", "PATCH", "DELETE")
SUMMAYR_CHT_REQUEST_METHODS = ("GET",)

CHAT_BOT_USE_SPACE = "chat_group_biz"
COMMUNITY_RUN_VER = "open"

REDIS_BIZ_INFO_PREFIX = f"{BKCHAT_CACHE_PREFIX}_cc_biz_info"
