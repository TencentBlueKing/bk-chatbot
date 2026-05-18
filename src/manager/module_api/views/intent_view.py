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
from blueapps.account.decorators import login_exempt
from blueapps.utils.logger import logger
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from iam import IAM, Action, Request, Subject
from rest_framework.decorators import action
from rest_framework.response import Response

from common.drf.view_set import BaseUpdateViewSet
from common.perm.permission import check_permission
from src.manager.module_api.enums import UpdateAvailableUserAction
from src.manager.module_api.proto.intent import (
    IntentAvailableUserSerializer,
    IntentGWSerializer,
    IntentListByBizSerializer,
    intent_update_docs,
    intent_gw_update_available_user_docs,
    intent_gw_list_docs,
)
from src.manager.module_intent.models import Intent


@method_decorator(name="update", decorator=intent_update_docs)
class IntentViewSet(BaseUpdateViewSet):
    """
    意图接入
    """

    queryset = Intent.objects.all()
    serializer_class = IntentGWSerializer

    @login_exempt
    @csrf_exempt
    @check_permission()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@method_decorator(name="update_available_user", decorator=intent_gw_update_available_user_docs)
@method_decorator(name="list", decorator=intent_gw_list_docs)
class GwIntentViewSet(BaseUpdateViewSet):
    """
    意图接入 - 对外网关接口（用户态鉴权）
    """

    queryset = Intent.objects.all()
    serializer_class = IntentGWSerializer

    @login_exempt
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        根据 biz_id 查询意图列表
        支持按 intent_name（模糊）、status 过滤
        """
        serializer = IntentListByBizSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data

        filters = {"biz_id": params["biz_id"], "is_deleted": False}

        queryset = Intent.objects.filter(**filters).order_by("-updated_at")
        data = IntentGWSerializer(queryset, many=True).data
        return Response({"result": True, "data": data})

    @action(detail=True, methods=["post"])
    def update_available_user(self, request, *args, **kwargs):
        """
        修改意图可执行用户
        鉴权：网关 JWT 用户态鉴权 + IAM 校验 username 的业务权限
        """
        intent = self.get_object()
        return self._update_available_user(request, intent)

    def _update_available_user(self, request, intent):
        """
        公共逻辑：修改意图可执行用户
        从 request.user.username 获取操作人，通过 IAM 校验业务权限后更新 available_user
        """
        serializer = IntentAvailableUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.user.username
        available_user_set = set(serializer.validated_data["available_user"])
        act = serializer.validated_data["action"]

        # IAM 查询 username 有权限的 biz_id 列表
        try:
            iam_ins = IAM(
                settings.APP_CODE,
                settings.SECRET_KEY,
                bk_apigateway_url=f"{settings.BK_API_URL_TMPL.format(api_name='bk-iam')}/prod",
            )
            iam_request = Request("bkchat_saas", Subject("user", username), Action("biz_management"), [], None)
            policies = iam_ins._do_policy_query(iam_request)
            logger.info(f"[update_available_user] {username} iam policies -> {policies}")
            _bk_biz_id_list = policies["value"] if isinstance(policies["value"], list) else [policies["value"]]
            bk_biz_id_list = [int(biz_id) for biz_id in _bk_biz_id_list]
        except Exception:
            logger.exception(f"[update_available_user] IAM query failed for user {username}")
            raise Exception("IAM 权限查询失败")

        # 鉴权
        if intent.biz_id not in bk_biz_id_list:
            logger.warning(f"[update_available_user] user {username} has no permission to update intent {intent.id}")
            raise Exception(f"用户{username}无权限执行此操作")

        # 更新 available_user
        if act == UpdateAvailableUserAction.ADD.value:
            intent.available_user = list(set(intent.available_user) | available_user_set)
        else:
            intent.available_user = list(set(intent.available_user) - available_user_set)
        intent.action = act
        intent.updated_by = username
        intent.save(update_fields=["available_user", "updated_by", "updated_at"])

        logger.info(
            f"[update_available_user] intent {intent.id} available_user updated by {username} -> "
            f"{intent.available_user}"
        )
        return Response({"data": {"id": intent.id, "available_user": intent.available_user}})
