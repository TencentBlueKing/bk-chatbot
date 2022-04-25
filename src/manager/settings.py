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

import os

current_dir = os.path.dirname(__file__)

# 存在路由(urls.py)的APP
BKCHAT_APPS = list(
    filter(
        lambda x: "module_" in x and "urls.py" in os.listdir(f"{current_dir}/{x}"),
        os.listdir(current_dir),
    )
)
# bkchat注册APP
BKCHAT_INSTALLED_APPS = tuple(map(lambda x: f"src.manager.{x}", BKCHAT_APPS))

# 包含定时任务的APP
TASK_DIR_APP_LIST = list(
    filter(
        lambda x: "module_" in x and "tasks" in os.listdir(f"{current_dir}/{x}"),
        os.listdir(current_dir),
    )
)
# 配置celery定时任务
CHILD_CELERY_IMPORTS = []
for app in TASK_DIR_APP_LIST:
    for child_dir in os.listdir(f"{current_dir}/{app}/tasks"):
        if "_timer.py" in child_dir:
            new_dir = child_dir.replace(".py", "")
            CHILD_CELERY_IMPORTS.append(f"src.manager.{app}.tasks.{new_dir}")
CHILD_CELERY_IMPORTS = tuple(CHILD_CELERY_IMPORTS)
