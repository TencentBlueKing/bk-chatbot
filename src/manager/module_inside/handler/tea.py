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
from src.manager.handler.in_api.youti_api import MgaAPI


def get_product_users(cc_id):
    """
    获取产品
    @param cc_id:
    @return:
    """
    data = {"cc_id": cc_id}
    result = MgaAPI().get_cp(**data)
    return result.get("data")


async def get_departments(wx_union_id):
    """
    获取用户部门
    @return:
    """
    data = {"union_id": wx_union_id}
    result = MgaAPI().get_user_info(**data)
    return result.get("data")
