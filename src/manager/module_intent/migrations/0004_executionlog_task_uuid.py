# Generated by Django 2.2.16 on 2022-10-27 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module_intent', '0003_executionlog_notice_exec_success'),
    ]

    operations = [
        migrations.AddField(
            model_name='executionlog',
            name='task_uuid',
            field=models.CharField(default='', max_length=256, verbose_name='uuid'),
        ),
    ]
