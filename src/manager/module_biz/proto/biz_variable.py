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


from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers

from common.utils.pwd import AESClassicCipher, gen_pwd
from src.manager.module_biz.models import BizVariableModel

biz_variable_tag = ["业务全局变量"]


class AseKey:
    def set_context(self, instance):
        """
        设置默认值
        """
        self.ase_key = gen_pwd(12)

    def __call__(self, *args, **kwargs):
        return self.ase_key

    def __repr__(self):
        return


class BizVariableViewSerializer(serializers.ModelSerializer):
    """
    全局变量验证器
    """

    value = serializers.SerializerMethodField()
    ase_key = serializers.HiddenField(default=AseKey())

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


class ReqPostBizVariableViewSerializer(BizVariableViewSerializer):
    """
    全局变量验证器
    """

    value = serializers.CharField()

    def create(self, validated_data: dict):
        """
        添加
        @param validated_data:
        @return:
        """

        # 如果是密码类型进行加密处理
        if validated_data.get("type") == "password":
            key = validated_data.get("ase_key")
            value = validated_data.get("value")
            # 进行对称加密
            aes_cipher = AESClassicCipher(key)
            encrypt_text = aes_cipher.encrypt(value)
            validated_data["value"] = encrypt_text

        return super(BizVariableViewSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        """
        设置
        @param instance:
        @param validated_data:
        @return:
        """
        # 如果是密码类型进行加密处理
        if validated_data.get("type") == "password":
            key = validated_data.get("ase_key")
            value = validated_data.get("value")
            # 进行对称加密
            aes_cipher = AESClassicCipher(key)
            encrypt_text = aes_cipher.encrypt(value)
            validated_data["value"] = encrypt_text
        return super().update(instance, validated_data)


########################################

biz_variable_list_docs = swagger_auto_schema(
    tags=biz_variable_tag,
    operation_id="全局变量-查询",
)

biz_variable_create_docs = swagger_auto_schema(
    tags=biz_variable_tag,
    operation_id="全局变量-添加",
)

biz_variable_update_docs = swagger_auto_schema(
    tags=biz_variable_tag,
    operation_id="全局变量-修改",
)

biz_variable_delete_docs = swagger_auto_schema(
    tags=biz_variable_tag,
    operation_id="全局变量-删除",
)
