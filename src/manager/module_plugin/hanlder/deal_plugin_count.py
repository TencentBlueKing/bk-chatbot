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
from common.constants import PROD_PLUGIN_URI_ENV
from common.utils.time import mk_now_before_day
from handler.in_api.plugin import PluginManage

OPEN_PLUGIN_HTTP = "OPEN_PLUGIN_HTTP"


def get_plugin_exec(n=None):
    """
    获取执行次数
    @return:
    """
    plugin_manage = PluginManage(PROD_PLUGIN_URI_ENV)

    if n is None:
        # 插件框架中心获取数据
        exec_count_ret = plugin_manage.get_exec_count()
    else:
        exec_count_ret = plugin_manage.get_exec_count(
            s_time=mk_now_before_day(n),
        )
    #
    data_dict = exec_count_ret.get("data")
    new_dict = {k.replace(f"{OPEN_PLUGIN_HTTP}_", ""): v for k, v in data_dict.items() if OPEN_PLUGIN_HTTP in k}
    return new_dict
