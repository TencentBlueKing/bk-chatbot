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


from adapter.api import CCApi
from common.requests.batch import batch_request


class CC:
    """
    cc接口
    """

    @classmethod
    def search_business(self, bk_username, biz_ids: list = None, fields=None, **kwargs):
        """
        业务信息查询
        @param bk_username:  用户名称
        @param biz_ids:      业务id列表
        @param fields:       查询字段
        @param kwargs:       自定义查询字段biz_property_filter优先级高于biz_id
        @return:
        """
        params = {
            "bk_username": bk_username,
            "fields": fields,
        }

        # 通过业务ID列表查询
        if biz_ids:
            params.setdefault(
                "biz_property_filter",
                {"condition": "AND", "rules": [{"field": "bk_biz_id", "operator": "in", "value": biz_ids}]},
            )
        # 通过自定义属性进行查询
        biz_property_filter = kwargs.get("biz_property_filter")
        if biz_property_filter:
            params.setdefault("biz_property_filter", biz_property_filter)
        data = CCApi.search_business(params)
        info = data.get("info", [])
        return info

    @classmethod
    def list_biz_hosts(cls, bk_username, query_params):
        """查询主机列表:V3"""
        params = {
            "bk_username": bk_username,
            "bk_biz_id": query_params.get("biz_id"),
            "fields": [
                "bk_cloud_id",
                "bk_os_name",
                "bk_host_name",
                "bk_logic_zone",
                "operator",
                "bk_svr_device_cls_name",
                "bk_host_innerip",
                "bk_host_outerip",
                "idc_name",
                "bk_service_arr",
                "srv_status",
                "module_name",
                "bk_bak_operator",
            ],
            "page": {"start": 0, "limit": 500, "sort": "bk_host_innerip"},
        }

        set_ids = query_params.get("set_ids")
        module_ids = query_params.get("module_ids")
        ip_keyword = query_params.get("ip_keyword")

        if set_ids:
            params.update(bk_set_ids=set_ids)

        if module_ids:
            params.update(bk_module_ids=module_ids)

        if ip_keyword:
            params.update(
                host_property_filter={
                    "condition": "AND",
                    "rules": [
                        {
                            "field": "bk_host_innerip",
                            "operator": "contains",
                            "value": ip_keyword,
                        }
                    ],
                }
            )

        data = batch_request(CCApi.list_biz_hosts, params)
        return data

    @classmethod
    def search_biz_inst_topo(cls, bk_username, query_params):
        """查询业务拓扑:V3"""

        res = CCApi.search_biz_inst_topo(
            {
                "bk_biz_id": query_params.get("biz_id"),
                "bk_username": bk_username,
                "level": -1,
            }
        )

        if res:
            return res[0]["child"]

        return []
