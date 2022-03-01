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
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action
from rest_framework.response import Response

from common.constants import TIMER_MAX_NUM
from common.drf.view_set import (
    BaseCreateViewSet,
    BaseDelViewSet,
    BaseGetViewSet,
    BaseUpdateViewSet,
)
from common.perm.permission import check_permission
from module_timer.hanlder.deal_timer import deal_timer, update_timer_status
from module_timer.models import TimerModel
from module_timer.proto.timer import (
    ReqPutTimerSerializer,
    TimerSerializer,
    timer_callback_docs,
    timer_create_docs,
    timer_del_docs,
    timer_list_docs,
    timer_update_docs,
)
from module_timer.tasks.callback import callback


@method_decorator(name="list", decorator=timer_list_docs)
@method_decorator(name="create", decorator=timer_create_docs)
@method_decorator(name="update", decorator=timer_update_docs)
@method_decorator(name="destroy", decorator=timer_del_docs)
@method_decorator(name="callback", decorator=timer_callback_docs)
class TimerViewSet(BaseGetViewSet, BaseCreateViewSet, BaseUpdateViewSet, BaseDelViewSet):
    queryset = TimerModel.objects.all()
    serializer_class = TimerSerializer
    update_serializer_class = ReqPutTimerSerializer
    filterset_class = TimerModel.OpenApiFilter

    @login_exempt
    @csrf_exempt
    @check_permission()
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        添加定时任务
        """

        # 单业务创建
        biz_id = serializer.validated_data.get("biz_id", 0)
        count = TimerModel.objects.filter(biz_id=biz_id).count()
        if count >= TIMER_MAX_NUM:
            raise ValueError(f"项目ID: {biz_id} 已经创建{TIMER_MAX_NUM} 个定时任务")
        with transaction.atomic():
            timer_obj = deal_timer(serializer)
            # 更新定时任务状态
            update_timer_status(timer_obj.job_timer_id, timer_obj.timer_status)

    def perform_update(self, serializer):
        """
        更新定时任务
        @param serializer:
        @return:
        """

        instance: TimerModel = serializer.instance
        old_status = instance.timer_status

        # 执行
        super().perform_create(serializer)
        if old_status != instance.timer_status:
            # 更新定时任务状态
            update_timer_status(
                instance.job_timer_id,
                instance.timer_status,
            )

    def perform_destroy(self, instance: TimerModel):
        """
        定时任务删除
        @param instance:
        @return:
        """

        # 置为关闭状态之后删除
        instance.timer_status = TimerModel.TimerStatus.CLOSE.value
        update_timer_status(
            instance.job_timer_id,
            instance.timer_status,
        )
        instance.save()
        if not instance.timer_status == TimerModel.TimerStatus.CLOSE.value:
            raise ValueError("timer status is not 2")
        instance.delete()

    @action(detail=False, methods=["POST"])
    def callback(self, request, *args, **kwargs):
        """
        定时任务回调接口
        """

        payload = request.payload
        id = payload.get("id")
        celery_data = callback.delay(id)
        return Response({"data": celery_data.id})
