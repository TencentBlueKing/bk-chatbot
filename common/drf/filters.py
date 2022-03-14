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

import django_filters
from django_filters import filters
from django.db.models import Q


class BaseOpenApiFilter(django_filters.FilterSet):
    """
    基础过滤
    """

    created_at_min = filters.CharFilter(field_name="created_at", lookup_expr="gte")
    created_at_max = filters.CharFilter(field_name="created_at", lookup_expr="lte")
    updated_at_min = filters.CharFilter(field_name="updated_at", lookup_expr="gte")
    updated_at_max = filters.CharFilter(field_name="updated_at", lookup_expr="lte")


    def self_or(self, queryset, field_name, value):
        """
        自定义 或操作
        """

        if not hasattr(self, "or_groups"):
            setattr(self, "or_groups", {})

        field_filter = self.filters.get(field_name)
        if hasattr(field_filter, "lookup_expr"):
            lookup_expr = field_filter.lookup_expr
            field_name = f"{field_name}__{lookup_expr}"
        self.or_groups[field_name] = value
        return queryset

    def self_ignore(self, queryset, field_name, value):
        """
        忽视
        """
        return queryset

    @property
    def qs(self):
        base_queryset = super().qs
        if not hasattr(self, "or_groups"):
            return base_queryset
        query = Q()
        for k, v in self.or_groups.items():
            query |= Q(**{k: v})
        return base_queryset.filter(query)
