# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from ..base import BaseApi, ProxyDataAPI


class _CCApi(BaseApi):

    MODULE = _("配置平台")

    def __init__(self):

        self.search_business = ProxyDataAPI("查询业务列表")
        # CC3.0 接口
        self.search_inst_by_object = ProxyDataAPI("查询CC云区域ID")
        self.search_biz_inst_topo = ProxyDataAPI("查询业务TOPO，显示各个层级")
        self.search_service_instance = ProxyDataAPI("获取服务实例")
        self.search_module = ProxyDataAPI("查询模块")
        self.search_service_category = ProxyDataAPI("查询服务分类")
        self.get_biz_internal_module = ProxyDataAPI("查询内部主机模块")
        self.search_object_attribute = ProxyDataAPI("查询对象属性")
        self.get_biz_location = ProxyDataAPI("查询业务所在环境的CC版本")
        self.list_biz_hosts = ProxyDataAPI("查询业务下的主机")
        self.list_biz_hosts_topo = ProxyDataAPI("查询业务下的主机和拓扑信息")
        self.search_cloud_area = ProxyDataAPI("查询云区域")
        self.find_host_topo_relation = ProxyDataAPI("获取主机与拓扑的关系")
        self.search_set = ProxyDataAPI("查询集群")


CCApi = _CCApi()
