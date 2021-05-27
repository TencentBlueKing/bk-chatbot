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
import json
import zlib

from django.db import models
from django.utils.translation import ugettext_lazy as _

from common.constants import CHAT_BOT_TYPE_DEFAULT
from common.constants import CHAT_BOT_TYPES
from common.constants import TAK_PLATFORM_JOB
from common.constants import TASK_EXECUTE_STATUS_CHOICES
from common.constants import TASK_PLATFORM_CHOICES
from module_biz.models import BaseModel


class CompressJSONField(models.BinaryField):
    def __init__(self, compress_level=6, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compress_level = compress_level

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        return zlib.compress(json.dumps(value).encode("utf-8"), self.compress_level)

    def to_python(self, value):
        value = super().to_python(value)
        return json.loads(zlib.decompress(value).decode("utf-8"))

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)


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
    config = CompressJSONField(verbose_name=_("机器人配置"), default={})

    class Meta:
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
    available_user = CompressJSONField(verbose_name=_("可执行用户"), default=[])
    available_group = CompressJSONField(verbose_name=_("可执行群组"), default=[])
    is_commit = models.BooleanField(_("执行确认"), default=True)

    class Meta:
        verbose_name = _("【意图】")
        verbose_name_plural = _("【意图】")

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
    content = CompressJSONField(verbose_name=_("语料列表"), default=[])

    class Meta:
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
    task_id = models.CharField(
        _("任务ID"),
        default=TAK_PLATFORM_JOB,
        max_length=128,
    )
    activities = CompressJSONField(verbose_name=_("节点信息"), default=[])
    slots = CompressJSONField(verbose_name=_("槽位信息"), default=[])
    source = CompressJSONField(verbose_name=_("任务元数据"), default={})
    script = models.TextField(_("执行脚本信息"), default="")

    class Meta:
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
    执行日志
    """

    biz_id = models.PositiveIntegerField(_("业务ID"), default=0, db_index=True)
    intent_id = models.BigIntegerField(_("意图ID"), default=-1)
    intent_name = models.CharField(_("技能名称"), default="", max_length=128)
    bot_name = models.CharField(_("机器人名称"), default="", max_length=128)
    bot_type = models.CharField(_("机器人类型"), default="default", max_length=128)
    platform = models.CharField(_("平台名称"), default="JOB", max_length=128)
    task_id = models.CharField(_("任务ID"), default="JOB", max_length=128)
    sender = models.CharField(_("执行人"), default="", max_length=128)
    msg = models.TextField(_("调用信息"), default="")
    status = models.CharField(
        _("任务状态"),
        default="0",
        max_length=128,
        choices=TASK_EXECUTE_STATUS_CHOICES,
    )

    start_time = models.CharField(_("开始时间"), default="", max_length=256)
    end_time = models.CharField(_("结束时间"), default="", max_length=256)

    class Meta:
        verbose_name = _("【任务日志】")
        verbose_name_plural = _("【任务日志】")

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
        log = cls.objects.create(**kwargs)
        return log

    @classmethod
    def update_log(cls, log_id, **kwargs):
        """
        更新日志
        """
        cls.objects.filter(pk=log_id).update(**kwargs)
