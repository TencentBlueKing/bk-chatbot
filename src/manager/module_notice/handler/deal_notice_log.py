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

from common.utils.my_time import mk_now_time
from src.manager.handler.api.bk_base import BKBASE

BKAPP_NOTICE_LOG_TABLE = os.getenv("BKAPP_NOTICE_LOG_TABLE")  # 请求表


class NoticeLog:
    def __init__(self, biz_id, **kwargs):
        self.biz_id = biz_id  # 业务id
        self.page = kwargs.get("page", 1)  # 页码
        self.pagesize = kwargs.get("pagesize", 10)  # 每页数据
        self.the_date = mk_now_time("%Y%m%d")
        self.query = self.get_query(**kwargs)

    def get_query(self, **kwargs):
        """

        @param kwargs:
        @return:
        """
        query_list = [
            f"thedate <= '{self.the_date}'",
            f"`biz_id` = '{self.biz_id}'",
        ]

        # 查询结果
        send_result = kwargs.get("send_result")  # 告警结果
        if send_result:
            query_list.append(f"send_result = '{send_result}'")

        # 产寻消息来源
        msg_source = kwargs.get("msg_source")  # 消息源
        if msg_source:
            query_list.append(f"msg_source = '{msg_source}'")

        # 查询平台
        im_platform = kwargs.get("im_platform")  # 平台
        if im_platform:
            query_list.append(f"im_platform = '{im_platform}'")

        # 通过原始内容查询
        raw_data = kwargs.get("raw_data")  # 内容
        if raw_data:
            query_list.append(f"raw_data like '%%{im_platform}%%'")

        query = " AND ".join(query_list)

        return query

    def get_count(self):
        """
        获取数量
        @return:
        """

        sql = f"""
        SELECT
            count(*) AS num
        FROM
            {BKAPP_NOTICE_LOG_TABLE}
        WHERE
            {self.query}
        """

        # 请求数量
        ret = BKBASE.query_sync(sql)
        num = ret.get("list")[0].get("num") if len(ret.get("list")) == 1 else 0
        return num

    def get_data(self):
        """
        获取数据
        @return:
        """
        sql = f"""
SELECT
    msg_data,
    send_time,
    send_result,
    msg_source,
    group_name,
    biz_name,
    msg_type,
    im_platform,
    biz_id,
    raw_data
FROM
   {BKAPP_NOTICE_LOG_TABLE}
WHERE
   {self.query}
ORDER BY
    dtEventTime DESC
    LIMIT {self.pagesize} OFFSET {self.page}"""
        # 请求数量
        ret = BKBASE.query_sync(sql)
        value_list = ret.get("list")
        return value_list
