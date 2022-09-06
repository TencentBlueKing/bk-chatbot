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

from rest_framework.response import Response
from rest_framework.decorators import action

from common.drf.validation import validation
from common.drf.view_set import BaseViewSet
from common.perm.permission import login_exempt_with_perm
from common.utils.translation import TencentCloudClient
from src.manager.module_notice.proto.notice import (
    ChatReplyGWViewSerializer,
)


class ChatReplyGwViewSet(BaseViewSet):
    schema = None

    @login_exempt_with_perm
    @action(detail=False, methods=["POST"])
    @validation(ChatReplyGWViewSerializer)
    def reply(self, request, *args, **kwargs):
        payload = request.payload
        chat_content = payload.get("chat_content1")

        cli = TencentCloudClient()
        result = cli.chat(chat_content)
        if not result["result"]:
            return Response({"message": result["message"]}, exception=True)

        result.pop("result")
        return Response({"data": result})
