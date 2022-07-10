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


import json

from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from rest_framework.response import Response

from common.drf.decorator import get_cookie_biz_id
from common.drf.validation import validation
from common.drf.view_set import BaseManageViewSet, BaseViewSet
from common.http.request import get_request_biz_id
from common.perm.permission import login_exempt_with_perm
from src.manager.common.perm import check_biz_perm
from src.manager.handler.api.bk_chat import BkChat
from src.manager.module_notice.handler.action import DelAction, EditAction, SaveAction
from src.manager.module_notice.handler.deal_alarm_msg import OriginalAlarm
from src.manager.module_notice.handler.notice_cache import get_notices
from src.manager.module_notice.handler.other_alarm import OtherPlatformAlarm
from src.manager.module_notice.handler.strategy import PlatformStrategy
from src.manager.module_notice.models import AlarmStrategyModel
from src.manager.module_notice.proto.alarm import (
    AlarmConfigSerializer,
    ReqGetAlarmStrategySerializer,
    ReqPostAlarmConfigSerializer,
    ReqPutAlarmConfigSerializer,
    alarm_config_create_docs,
    alarm_config_delete_docs,
    alarm_config_list_docs,
    alarm_config_update_docs,
    alarm_strategy_list_docs,
    alarm_strategy_notice_docs,
)


@method_decorator(name="strategy", decorator=alarm_strategy_list_docs)
class AlarmViewSet(BaseViewSet):
    @action(detail=False, methods=["GET"])
    @validation(ReqGetAlarmStrategySerializer)
    def strategy(self, request, *args, **kwargs):
        """
        策略获取
        @return:
        """
        payload = request.payload
        biz_id = get_request_biz_id(request)
        platform = payload.get("platform")
        data = PlatformStrategy.get(int(platform), int(biz_id))
        return Response({"data": data})


@method_decorator(name="notice", decorator=alarm_strategy_notice_docs)
class AlarmNoticeViewSet(BaseViewSet):
    auto_schema = None

    @login_exempt_with_perm
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @action(detail=False, methods=["POST"])
    def notice(self, request, *args, **kwargs):
        """
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        payload = request.payload
        config_id = payload.get("config_id")
        notice_groups = get_notices(config_id)  # 需要通知的群组
        original_alarm = OriginalAlarm(payload)  # 原始告警
        for notice_group in notice_groups:
            im_type = notice_group.get("im")
            # 通过im获取不同
            params: dict = getattr(original_alarm, im_type.lower())()
            params.update(
                **{
                    "im": im_type,
                    "headers": notice_group.get("headers"),
                    "receiver": notice_group.get("receiver"),
                }
            )
            BkChat.new_send_msg(**params)
        return Response({"data": []})

    @action(detail=False, methods=["POST"])
    def original_notice(self, request, *args, **kwargs):
        """
        @param request:
        @param args:
        @param kwargs:
        @return:
        """
        payload = request.payload

        payload_data = payload.get("data")
        config_id = payload_data.get("config_id")
        notice_groups = get_notices(config_id)  # 需要通知的群组
        # 数据处理
        callback_message = json.loads(payload_data.get("callback_message"))
        original_alarm = OriginalAlarm(callback_message)  # 原始告警
        for notice_group in notice_groups:
            im_type = notice_group.get("im")
            # 通过im获取不同
            params: dict = getattr(original_alarm, im_type.lower())()
            params.update(
                **{
                    "im": im_type,
                    "headers": notice_group.get("headers"),
                    "receiver": notice_group.get("receiver"),
                }
            )
            BkChat.new_send_msg(**params)
        return Response({"data": []})


@method_decorator(name="list", decorator=alarm_config_list_docs)  # 文档装饰器
@method_decorator(name="create", decorator=alarm_config_create_docs)  # 文档装饰器
@method_decorator(name="update", decorator=alarm_config_update_docs)  # 文档装饰器
@method_decorator(name="destroy", decorator=alarm_config_delete_docs)  # 文档装饰器
@method_decorator(name="list", decorator=get_cookie_biz_id)  # 业务id作为cookice
@method_decorator(name="create", decorator=check_biz_perm)  # 判断是不是业务人员
@method_decorator(name="update", decorator=check_biz_perm)  # 判断是不是业务人员
@method_decorator(name="destroy", decorator=check_biz_perm)  # 判断是不是业务人员
class AlarmConfigViewSet(BaseManageViewSet):
    """
    告警配置
    """

    queryset = AlarmStrategyModel.objects.all()
    serializer_class = AlarmConfigSerializer
    create_serializer_class = ReqPostAlarmConfigSerializer
    update_serializer_class = ReqPutAlarmConfigSerializer
    filterset_class = AlarmStrategyModel.OpenApiFilter

    def perform_create(self, serializer):
        """
        添加告警配置
        @param serializer:
        @return:
        """

        # 处理套餐保存到对应的平台
        with transaction.atomic():
            data = serializer.validated_data
            params = {
                "biz_id": data.get("biz_id"),
                "name": data.get("deal_alarm_name"),
                "deal_strategy_value": data.get("deal_strategy_value"),
                "is_enabled": data.get("is_enabled"),
            }
            platform = data.get("alarm_source_type")
            config_id = SaveAction.save(int(platform), **params)
            # 更新数据
            serializer.validated_data["config_id"] = config_id
            serializer.save()
            strategy_ids = list(map(lambda x: int(x.get("id")), data.get("alarm_strategy")))
            alarm_class = OtherPlatformAlarm(
                biz_id=data.get("biz_id"),
                strategy_ids=strategy_ids,
                config_id=config_id,
                new_strategy_ids=strategy_ids,
            )
            # 处理套餐更新到对应的策略中
            alarm_class.update_strategy_action()

    def perform_update(self, serializer):
        """
        修改告警配置
        @param serializer:
        @return:
        """

        with transaction.atomic():
            pk = self.kwargs.get("pk")
            original_alarm_strategy_obj = AlarmStrategyModel.objects.get(pk=pk)
            # 原始套餐策略
            original_strategy_ids = list(
                map(
                    lambda x: int(x.get("id")),
                    original_alarm_strategy_obj.alarm_strategy,
                )
            )
            serializer.save()
            alarm_strategy_obj = AlarmStrategyModel.objects.get(pk=pk)
            params = {
                "biz_id": alarm_strategy_obj.biz_id,
                "name": alarm_strategy_obj.deal_alarm_name,
                "deal_strategy_value": alarm_strategy_obj.deal_strategy_value,
                "config_id": int(alarm_strategy_obj.config_id),
                "is_enabled": alarm_strategy_obj.is_enabled,
            }
            # 编辑套餐
            EditAction.edit(alarm_strategy_obj.alarm_source_type, **params)

            # 新策略ID
            new_alarm_strategy = serializer.validated_data.get("alarm_strategy")
            new_strategy_ids = (
                list(
                    map(
                        lambda x: int(x.get("id")),
                        new_alarm_strategy,
                    )
                )
                if new_alarm_strategy
                else original_strategy_ids
            )
            strategy_ids = list(set(original_strategy_ids + new_strategy_ids))
            alarm_class = OtherPlatformAlarm(
                biz_id=alarm_strategy_obj.biz_id,
                strategy_ids=strategy_ids,
                new_strategy_ids=new_strategy_ids,
                config_id=int(alarm_strategy_obj.config_id),
            )

            if set(new_strategy_ids) != set(original_strategy_ids):
                # 套餐添加
                alarm_class.update_strategy_action()

    def perform_destroy(self, instance):
        """
        删除告警配置
        @param instance:
        @return:
        """

        strategy_ids = list(map(lambda x: int(x.get("id")), instance.alarm_strategy))
        alarm_class = OtherPlatformAlarm(
            biz_id=instance.biz_id,
            strategy_ids=strategy_ids,
            new_strategy_ids=[],
            config_id=int(instance.config_id),
        )
        # 更新关联的策略
        alarm_class.update_strategy_action()
        # 删除处理套餐
        try:
            DelAction.delete(int(instance.alarm_source_type), config_id=int(instance.config_id))
        except Exception:
            pass
        instance.delete()
