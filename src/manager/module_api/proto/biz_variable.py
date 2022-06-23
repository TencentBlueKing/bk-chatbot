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


from rest_framework import serializers

from common.utils.pwd import AESClassicCipher
from src.manager.module_biz.models import BizVariableModel

biz_variable_tag = ["业务全局变量"]


class APIBizVariableViewSerializer(serializers.ModelSerializer):
    """
    全局变量验证器
    """

    value = serializers.SerializerMethodField()

    def get_value(self, obj):
        # 这里可以通过obj进行一些处理获取销售量然后返回
        value = obj.value
        if obj.type == "password":
            try:
                key = obj.ase_key
                aes_cipher = AESClassicCipher(key)
                value = aes_cipher.decrypt(value)
                return value
            except:  # pylint: disable=broad-except
                pass
        return value

    class Meta:
        model = BizVariableModel
        fields = ["id", "key", "biz_id", "name", "value", "type", "ase_key"]
