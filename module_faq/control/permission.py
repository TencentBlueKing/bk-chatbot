# -*- coding: utf-8 -*-
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
from rest_framework import permissions

from common.utils.users import get_request_user
from module_faq.models import FAQ


class FaqPermission(permissions.BasePermission):
    """
    知识库权限控制
    """

    def has_permission(self, request, view):
        data = FAQ.query_faq_list(member__contains=get_request_user(request))

        if not data:
            return False

        return True
