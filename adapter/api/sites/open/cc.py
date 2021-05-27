# -*- coding: utf-8 -*-
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

from django.utils.translation import ugettext_lazy as _

from adapter.api.base import DataAPI
from adapter.api.modules.utils import add_esb_info_before_request
from config.domains import CC_APIGATEWAY_ROOT_V2


class _CCApi(object):
    MODULE = _("配置平台")

    def __init__(self):
        self.search_business = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_business/",
            module=self.MODULE,
            description="查询业务列表",
            before_request=add_esb_info_before_request,
            cache_time=60,
        )
        self.search_inst_by_object = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_inst_by_object/",
            module=self.MODULE,
            description="查询CC对象列表",
            before_request=add_esb_info_before_request,
        )
        self.search_biz_inst_topo = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_biz_inst_topo/",
            module=self.MODULE,
            description="查询业务TOPO，显示各个层级",
            before_request=add_esb_info_before_request,
        )
        self.search_module = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_module",
            module=self.MODULE,
            description="查询模块",
            before_request=add_esb_info_before_request,
        )
        self.get_host_info = DataAPI(
            method="GET",
            url=CC_APIGATEWAY_ROOT_V2 + "search_module",
            module=self.MODULE,
            description="查询模块",
            before_request=add_esb_info_before_request,
        )
        self.get_biz_internal_module = DataAPI(
            method="GET",
            url=CC_APIGATEWAY_ROOT_V2 + "get_biz_internal_module",
            module=self.MODULE,
            description="查询内部业务模块",
            before_request=add_esb_info_before_request,
        )
        self.search_object_attribute = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_object_attribute",
            module=self.MODULE,
            description="查询对象属性",
            before_request=add_esb_info_before_request,
        )
        self.list_biz_hosts = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "list_biz_hosts",
            module=self.MODULE,
            description="查询业务下的主机",
            before_request=add_esb_info_before_request,
        )
        self.list_biz_hosts_topo = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "list_biz_hosts_topo",
            module=self.MODULE,
            description="查询业务下的主机和拓扑信息",
            before_request=add_esb_info_before_request,
        )
        self.search_cloud_area = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_cloud_area",
            module=self.MODULE,
            description="查询云区域",
            before_request=add_esb_info_before_request,
        )
        self.find_host_topo_relation = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "find_host_topo_relation",
            module=self.MODULE,
            description="获取主机与拓扑的关系",
            before_request=add_esb_info_before_request,
        )
        self.search_set = DataAPI(
            method="POST",
            url=CC_APIGATEWAY_ROOT_V2 + "search_set",
            module=self.MODULE,
            description="查询集群",
            before_request=add_esb_info_before_request,
        )

    def get_biz_location(self, *args, **kwargs):
        return []


CCApi = _CCApi()
