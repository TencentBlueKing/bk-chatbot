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

import time

from rest_framework import serializers

from common.http.request import get_request_biz_id
from common.utils.str import camel_to_snake


class DefaultFiled:
    def __init__(self):
        """
        初始化
        @return:
        """

        self.attribute_name = camel_to_snake(self.__class__.__name__)
        super().__init__()

    def __call__(self, *args, **kwargs):
        """
        通过类名获取数据
        @param args:
        @param kwargs:
        @return:
        """
        attribute = camel_to_snake(self.attribute_name)
        value = getattr(self, attribute)
        return value

    def __repr__(self):
        return


class BizId(DefaultFiled):
    def set_context(self, instance):
        """
        设置默认值
        """

        setattr(
            self,
            self.attribute_name,
            get_request_biz_id(instance.context["request"]),
        )


class TimeStampSerializer(serializers.CharField):
    """
    时间戳字段
    """

    def to_representation(self, value):
        """
        Serialize the object's class name.
        """
        execute_time = value
        if execute_time != "":
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(value)))
        return value
