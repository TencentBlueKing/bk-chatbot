# Generated by Django 2.2.16 on 2022-08-31 12:49

import common.models.base
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module_notice', '0006_taskbroadcast'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskbroadcast',
            name='start_time',
            field=common.models.base.FormatDateTimeField(auto_now_add=True, null=True, verbose_name='开始播报时间'),
        ),
        migrations.AlterField(
            model_name='taskbroadcast',
            name='step_id',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='任务当前步骤ID'),
        ),
        migrations.AlterField(
            model_name='taskbroadcast',
            name='step_status',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='当前步骤状态'),
        ),
        migrations.AlterField(
            model_name='taskbroadcast',
            name='stop_time',
            field=common.models.base.FormatDateTimeField(blank=True, null=True, verbose_name='终止播报时间'),
        ),
        migrations.AlterField(
            model_name='taskbroadcast',
            name='stop_user',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='终止播报人'),
        ),
    ]
