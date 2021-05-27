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
            name="FAQ",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("biz_id", models.PositiveIntegerField(default=0, verbose_name="业务ID")),
                (
                    "biz_name",
                    models.CharField(default="", max_length=128, verbose_name="业务名称"),
                ),
                (
                    "faq_name",
                    models.CharField(default="", max_length=128, verbose_name="知识库名称"),
                ),
                (
                    "faq_db",
                    models.CharField(default="", max_length=128, verbose_name="知识库DB"),
                ),
                (
                    "faq_collection",
                    models.CharField(default="", max_length=128, verbose_name="知识库表名"),
                ),
                (
                    "num",
                    models.CharField(default="", max_length=128, verbose_name="QA数量"),
                ),
                ("member", models.TextField(default="", verbose_name="维护人员")),
                ("is_delete", models.BooleanField(default=False, verbose_name="是否已删除")),
                (
                    "create_by",
                    models.CharField(default="-", max_length=100, verbose_name="创建人"),
                ),
                (
                    "update_time",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
            ],
            options={
                "verbose_name": "【知识库】",
                "verbose_name_plural": "【知识库】",
            },
        ),
    ]
