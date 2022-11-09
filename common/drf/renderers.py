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

import uuid

from rest_framework.renderers import JSONRenderer


class ResponseFormatRenderer(JSONRenderer):
    def render(self, data, media_type=None, renderer_context=None):
        data = self.format_data(data, renderer_context)
        return super().render(data, media_type, renderer_context)

    def format_data(self, data, renderer_context):
        data["request_id"] = str(uuid.uuid4())
        data["result"] = False if renderer_context["response"].exception else True
        data["code"] = 1 if renderer_context["response"].exception else 0
        data["message"] = data.get("message") if data.get("message", None) else renderer_context["response"].status_text
        return data
