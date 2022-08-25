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
import pandas as pd
from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response

from common.drf.view_set import BaseViewSet
from common.http.request import get_request_biz_id, get_request_user
from src.manager.handler.api.bk_cc import CC
from src.manager.module_intent.models import ExecutionLog

# 需要查询的用户列表
user_arr = ["bk_biz_developer", "bk_biz_maintainer", "bk_biz_productor", "bk_biz_tester"]

# 默认回退数据
default_data = [
    {"item:": v, "value": 0, "percent": 0}
    for v in ["bk_biz_developer", "bk_biz_maintainer", "bk_biz_productor", "bk_biz_tester"]
]


class UserExecViewSet(BaseViewSet):
    # schema = None

    def __get_exec_info(self, biz_user_info, queryset):
        """
        获取执行数据
        @param biz_user_info: 用户信息
        @param queryset:      执行数据
        @return:
        """
        # 对用户信息表处理
        user_info_arr = []
        for k, v in biz_user_info.items():
            if k not in user_arr:
                continue
            if v is None:
                v = ""
            user_info_arr += [{"name": name, "item": k} for name in v.split(",")]

        # 利用pandas 处理数据
        df_user_info = pd.DataFrame(user_info_arr)
        df_queryset = pd.DataFrame(queryset)
        df = df_user_info.merge(df_queryset, how="left", left_on="name", right_on="sender")
        # 聚类
        df_group = df.groupby("item").agg({"item": "first", "value": "sum"})
        # 求百分比
        df_group["percent"] = 100 * (df_group["value"] / df_group["value"].sum())

        # 转为int
        df_group["value"] = df_group["value"].astype(int)
        # 为空数据填充
        df_group["percent"] = df_group["percent"].fillna(value=0)
        ret = df_group.to_dict("records")
        return ret

    @action(detail=False, methods=["GET"])
    def exec_info(self, request, *args, **kwargs):
        username = get_request_user(request)
        biz_id = get_request_biz_id(request)

        # 本地查询，如果为空快速返回
        queryset = ExecutionLog.objects.filter(biz_id=biz_id).values("sender").annotate(value=Count("id"))

        # 为空快速返回
        if len(queryset) == 0:
            return Response({"data": default_data})

        data = CC().search_business(
            bk_username=username,
            biz_ids=[int(biz_id)],
            fields=user_arr,
        )
        # 判断是否有该业务存在
        if len(data) != 1:
            raise ValueError("查询的业务数量不为1")

        # 实际处理数据
        result = self.__get_exec_info(data[0], queryset)
        return Response({"data": result})
