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

import datetime

from celery.task import periodic_task

from src.manager.module_plugin.hanlder.deal_plugin_count import get_plugin_exec
from src.manager.module_plugin.models import Plugin


@periodic_task(run_every=datetime.timedelta(seconds=10))
def update_plugin_exec_num():
    """
    更新执行数量
    @return:
    """

    # 获取到对应的数据
    exec_count_dict = get_plugin_exec()  # 执行总次数
    lately_count_dict = get_plugin_exec(30)  # 近期执行次数

    # 保存数据
    plugin_obj_list = Plugin.objects.all()
    for plugin_obj in plugin_obj_list:
        plugin_key = plugin_obj.plugin_key
        # 数据处理
        exec_count = exec_count_dict.get(plugin_key, 0)  # 执行总次数
        lately_count = lately_count_dict.get(plugin_key, 0)  # 近期执行次数
        if exec_count:
            plugin_obj.plugin_exec_count = exec_count
        if lately_count:
            plugin_obj.plugin_lately_count = lately_count
        plugin_obj.save()
