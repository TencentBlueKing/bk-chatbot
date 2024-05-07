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
from enum import Enum

import django_filters
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_filters import filters

from common.constants import (
    CHAT_BOT_TYPE_DEFAULT,
    CHAT_BOT_TYPES,
    TAK_PLATFORM_JOB,
    TASK_PLATFORM_CHOICES,
    IntentMatchPattern,
)
from common.drf.filters import BaseOpenApiFilter
from common.models.base import BaseModel
from common.models.json import DictCharField
from common.utils.m_uuid import get_uuid4


class Bot(BaseModel):
    """
    机器人
    """

    biz_id = models.PositiveIntegerField(_("业务ID"), default=0, db_index=True)
    biz_name = models.CharField(_("业务名称"), default="", max_length=128)
    bot_id = models.CharField(_("机器人ID"), default="", max_length=128)
    bot_name = models.CharField(_("机器人名称"), default="", max_length=128)
    bot_type = models.CharField(
        _("机器人类型"),
        default=CHAT_BOT_TYPE_DEFAULT,
        max_length=128,
        choices=CHAT_BOT_TYPES,
    )
    config = DictCharField(verbose_name=_("机器人配置"), default={})

    class Meta:
        db_table = "tab_bot"
        verbose_name = _("【机器人】")
        verbose_name_plural = _("【机器人】")

    @classmethod
    def create_bot(cls, **kwargs):
        """
        创建机器人
        """
        return cls.objects.get_or_create(**kwargs)

    @classmethod
    def query_bot_list(cls, **kwargs):
        """
        获取机器人
        """
        return list(cls.objects.filter(**kwargs).order_by("-id").values())

    @classmethod
    def update_bot(cls, bot_id, **kwargs):
        """
        更新机器人
        """
        cls.objects.filter(pk=bot_id).update(**kwargs)

    @classmethod
    def bulb_update_bot(cls, bot_ids, **kwargs):
        """
        批量更新机器人
        """
        cls.objects.filter(pk__in=bot_ids).update(**kwargs)


class Intent(BaseModel):
    """
    用户意图
    """

    index_id = models.BigIntegerField(_("索引ID"), default=-1)
    biz_id = models.PositiveIntegerField(_("业务ID"), default=0, db_index=True)
    intent_name = models.CharField(_("技能名称"), default="", max_length=128)
    status = models.BooleanField(_("意图状态"), default=True)
    available_user = DictCharField(verbose_name=_("可执行用户"), default=[])
    available_group = DictCharField(verbose_name=_("可执行群组"), default=[])
    is_commit = models.BooleanField(_("执行确认"), default=True)
    notice_discern_success = models.BooleanField(_("识别成功通知"), default=True)
    notice_start_success = models.BooleanField(_("启动成功通知"), default=True)
    notice_exec_success = models.BooleanField(_("启动成功通知"), default=True)
    notice_single = models.BooleanField(_("通知个人"), default=False)
    serial_number = models.CharField(_("序列号"), default="-1", max_length=128)
    developer = DictCharField(_("开发商"), default=[])
    approver = DictCharField(_("审批人"), default=[])
    tag_name = models.CharField(verbose_name=_("标签分类"), max_length=128, default="")
    match_pattern = models.IntegerField(verbose_name=_("技能匹配模式"), default=IntentMatchPattern.LIKE.value)

    class Meta:
        db_table = "tab_intent"
        verbose_name = _("【意图】")
        verbose_name_plural = _("【意图】")

    class OpenApiFilter(django_filters.FilterSet):
        """
        提供给rest查询使用
        """

        biz_id = filters.CharFilter(field_name="biz_id")
        intent_name = filters.CharFilter(field_name="intent_name", lookup_expr="contains")
        status = filters.BooleanFilter(field_name="status")
        is_commit = filters.BooleanFilter(field_name="is_commit")
        created_by = filters.CharFilter(field_name="created_by")
        serial_number = filters.CharFilter(field_name="serial_number")
        developer = filters.CharFilter(field_name="developer", lookup_expr="contains")
        approver = filters.CharFilter(field_name="approver", lookup_expr="contains")
        available_user = filters.CharFilter(field_name="available_user", lookup_expr="contains")
        available_group = filters.CharFilter(field_name="available_group", lookup_expr="contains")

    @classmethod
    def query_intent_list(cls, **kwargs):
        """
        获取意图
        """
        return list(cls.objects.filter(**kwargs).order_by("-id").values())

    @classmethod
    def create_intent(cls, **kwargs):
        """
        创建意图
        """
        return cls.objects.get_or_create(**kwargs)

    @classmethod
    def update_intent(cls, intent_id, **kwargs):
        """
        更新意图
        """
        cls.objects.filter(pk=intent_id).update(**kwargs)

    @classmethod
    def bulk_update_intent(cls, intent_ids, **kwargs):
        """
        批量更新意图
        """
        cls.objects.filter(pk__in=intent_ids).update(**kwargs)


class Utterances(BaseModel):
    """
    语料信息
    """

    biz_id = models.PositiveIntegerField(_("业务ID"), default=0, db_index=True)
    index_id = models.BigIntegerField(_("索引ID"), default=-1)
    content = DictCharField(verbose_name=_("语料列表"), default=[])

    class Meta:
        db_table = "tab_intent_utterances"
        verbose_name = "【语料库】"
        verbose_name_plural = "【语料库】"

    @classmethod
    def query_utterances(cls, **kwargs):
        """
        获取语料
        """
        return list(cls.objects.filter(**kwargs).values())

    @classmethod
    def create_utterance(cls, **kwargs):
        """
        创建语料
        """
        cls.objects.create(**kwargs)

    @classmethod
    def update_utterance(cls, intent_id, **kwargs):
        """
        更新语料
        """
        cls.objects.filter(index_id=intent_id).update(**kwargs)


class Task(BaseModel):
    """
    任务
    """

    biz_id = models.PositiveIntegerField(_("业务ID"), default=0, db_index=True)
    index_id = models.BigIntegerField(_("索引ID"), default=-1)
    platform = models.CharField(
        _("平台名称"),
        default=TAK_PLATFORM_JOB,
        max_length=128,
        choices=TASK_PLATFORM_CHOICES,
    )
    task_id = models.CharField(_("任务ID"), default="", max_length=128)
    project_id = models.CharField(_("项目id"), default="", max_length=128)
    activities = DictCharField(verbose_name=_("节点信息"), default=[])
    slots = DictCharField(verbose_name=_("槽位信息"), default=[])
    source = DictCharField(verbose_name=_("任务元数据"), default={})
    script = models.TextField(_("执行脚本信息"), default="")

    class Meta:
        db_table = "tab_intent_task"
        verbose_name = _("【任务信息】")
        verbose_name_plural = _("【任务信息】")

    @classmethod
    def query_task_list(cls, **kwargs):
        """
        获取任务列表
        """
        return list(cls.objects.filter(**kwargs).values())

    @classmethod
    def create_task(cls, **kwargs):
        """
        创建任务
        """
        cls.objects.create(**kwargs)

    @classmethod
    def update_task(cls, intent_id, **kwargs):
        """
        更新语料
        """
        cls.objects.filter(index_id=intent_id).update(**kwargs)


class ExecutionLog(BaseModel):
    """
    意图执行日志
    """

    class PlatformType(Enum):
        """
        平台类型
        """

        DEFAULT = 0  # 默认
        JOB = 1  # 作业平台
        SOPS = 2  # 标准运维
        DEV_OPS = 3  # 蓝盾
        DEFINE = 4  # 自定义
        ITSM = 5  # ITSM

    class TaskExecStatus(Enum):
        INIT = 0  # 初始状态
        RUNNING = 1  # 执行中
        SUCCESS = 2  # 执行成功
        FAIL = 3  # 执行失败
        SUSPENDED = 4  # 暂停
        REMOVE = 5  # 执行异常

    biz_id = models.PositiveIntegerField(_("业务ID"), default=0, db_index=True)
    intent_id = models.BigIntegerField(_("意图ID"), default=-1)
    intent_name = models.CharField(_("技能名称"), default="", max_length=128)
    intent_create_user = models.CharField(_("意图添加人"), default="", max_length=128)
    bot_name = models.CharField(_("机器人名称"), default="", max_length=128)
    bot_type = models.CharField(_("机器人类型"), default="default", max_length=128)
    platform = models.IntegerField(
        _("平台类型"),
        default=PlatformType.DEFAULT.value,
        choices=[(tag.value, tag.name) for tag in PlatformType],
    )
    project_id = models.CharField(_("项目ID"), default="", max_length=128)
    feature_id = models.CharField(_("特色ID:蓝盾-流水线ID"), default="", max_length=128)
    task_id = models.CharField(_("任务ID"), default="", max_length=128)
    sender = models.CharField(_("执行人"), default="", max_length=128)
    rtx = models.CharField(_("rtx接受人"), default="", max_length=128)
    msg = models.TextField(_("调用信息"), default="")
    status = models.IntegerField(
        _("任务状态"),
        default=TaskExecStatus.INIT.value,
        choices=[(tag.value, tag.name) for tag in TaskExecStatus],
    )
    params = DictCharField("执行参数", default=[])
    notice_exec_success = models.BooleanField("执行成功是否通知", default=True)
    task_uuid = models.CharField(_("uuid"), default="", max_length=256)

    class Meta:
        db_table = "tab_intent_execution_log"
        verbose_name = _("【任务日志】")
        verbose_name_plural = _("【任务日志】")

    class OpenApiFilter(BaseOpenApiFilter):
        """
        提供给rest查询使用
        """

        id = filters.CharFilter(field_name="id")
        biz_id = filters.CharFilter(field_name="biz_id")
        intent_id = filters.CharFilter(field_name="intent_id")
        intent_name = filters.CharFilter(field_name="intent_name")
        bot_name = filters.CharFilter(field_name="bot_name")
        bot_type = filters.CharFilter(field_name="bot_type")
        platform = filters.CharFilter(field_name="platform")
        task_id = filters.CharFilter(field_name="task_id")
        sender = filters.CharFilter(field_name="sender")
        status = filters.CharFilter(field_name="status")
        bk_app_code = filters.CharFilter(field_name="bk_app_code", method="self_ignore")
        bk_app_secret = filters.CharFilter(field_name="bk_app_secret", method="self_ignore")

    @classmethod
    def query_log(cls, **kwargs):
        """
        获取任务记录
        :param kwargs:
        :return:
        """

        obj = cls.objects.filter(**kwargs).first()
        if not obj:
            raise ValueError("没有查询到对应的任务信息")
        return obj

    @classmethod
    def query_log_list(cls, **kwargs):
        """
        获取日志列表
        """
        return list(cls.objects.filter(**kwargs).values())

    @classmethod
    def create_log(cls, **kwargs):
        """
        创建日志
        """
        # 设置uuid
        kwargs.setdefault("task_uuid", get_uuid4())
        log = cls.objects.create(**kwargs)
        return log

    @classmethod
    def update_log(cls, log_id, **kwargs):
        """
        更新日志
        """
        cls.objects.filter(pk=log_id).update(**kwargs)


class IntentTag(BaseModel):
    """
    技能标签
    """

    biz_id = models.PositiveIntegerField(_("业务ID"), default=0, db_index=True)
    tag_name = models.CharField(_("标签名称"), max_length=128)
    tag_index = models.IntegerField(_("标签索引"))

    class Meta:
        db_table = "tab_intent_tag"
        verbose_name = _("【技能标签】")
        verbose_name_plural = _("【技能标签】")
        ordering = ("tag_index",)
