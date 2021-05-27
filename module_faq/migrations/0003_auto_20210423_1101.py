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

    dependencies = [
        ("module_faq", "0002_auto_20210423_1048"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="faq",
            name="updated_time",
        ),
        migrations.AddField(
            model_name="faq",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, null=True, verbose_name="创建时间"
            ),
        ),
        migrations.AddField(
            model_name="faq",
            name="deleted_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="删除时间"),
        ),
        migrations.AddField(
            model_name="faq",
            name="deleted_by",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="删除人"
            ),
        ),
        migrations.AddField(
            model_name="faq",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="描述"),
        ),
        migrations.AddField(
            model_name="faq",
            name="updated_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="更新时间"),
        ),
        migrations.AddField(
            model_name="faq",
            name="updated_by",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="更新人"
            ),
        ),
        migrations.AlterField(
            model_name="faq",
            name="created_by",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="创建人"
            ),
        ),
        migrations.AlterField(
            model_name="faq",
            name="is_deleted",
            field=models.BooleanField(default=False, verbose_name="是否删除"),
        ),
    ]
