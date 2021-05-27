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

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ChatGroupBusiness",
            fields=[
                (
                    "created_by",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="创建人"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, null=True, verbose_name="创建时间"
                    ),
                ),
                (
                    "updated_by",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="更新人"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="更新时间"),
                ),
                ("is_deleted", models.BooleanField(default=False, verbose_name="是否删除")),
                (
                    "deleted_by",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="删除人"
                    ),
                ),
                (
                    "deleted_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="删除时间"),
                ),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="描述"),
                ),
                (
                    "chat_group_id",
                    models.CharField(
                        default="-1",
                        max_length=255,
                        primary_key=True,
                        serialize=False,
                        verbose_name="群聊ID",
                    ),
                ),
                (
                    "chat_bot_type",
                    models.CharField(
                        choices=[
                            ("WEWORK", "企业微信"),
                            ("QQ", "QQ"),
                            ("WX", "微信"),
                            ("SLACK", "SLACK"),
                        ],
                        default="WEWORK",
                        max_length=50,
                        verbose_name="机器人类型",
                    ),
                ),
                ("biz_id", models.PositiveIntegerField(default=0, verbose_name="业务ID")),
                (
                    "biz_name",
                    models.CharField(default="", max_length=255, verbose_name="业务名称"),
                ),
            ],
            options={
                "verbose_name": "群ID绑定业务表",
                "verbose_name_plural": "群ID绑定业务表",
            },
        ),
    ]
