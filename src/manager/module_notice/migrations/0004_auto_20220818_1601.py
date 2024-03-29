# Generated by Django 2.2.16 on 2022-08-18 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module_notice', '0003_auto_20220727_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarmstrategymodel',
            name='is_translated',
            field=models.BooleanField(default=False, verbose_name='是否翻译'),
        ),
        migrations.AddField(
            model_name='alarmstrategymodel',
            name='translation_type',
            field=models.CharField(default='', max_length=32, verbose_name='目标语言'),
        ),
    ]
