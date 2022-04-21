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


from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers

from src.manager.module_other.models import VersionModel
from src.manager.module_other.proto import other_tag


class VersionSerializer(serializers.ModelSerializer):
    """
    version
    """

    context = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = VersionModel
        fields = ["id", "is_show", "version", "title", "context", "author", "updated_at"]


############################################################
version_list_docs = swagger_auto_schema(
    tags=other_tag,
    operation_id="version",
)
