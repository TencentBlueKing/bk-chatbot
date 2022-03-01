# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from adapter.api.base import DataAPI
from adapter.api.modules.utils import add_esb_info_before_request
from adapter.sites.ieod.config.domains import GSE_APIGATEWAY_ROOT_V2


def get_agent_status_before(params):
    hosts = [{"ip": ip_info["ip"], "bk_cloud_id": ip_info["plat_id"]} for ip_info in params["ip_infos"]]

    params = {
        "bk_supplier_account": "tencent",
        "hosts": hosts,
    }
    params = add_esb_info_before_request(params)
    return params


def get_agent_status_after(response_result):
    hosts = response_result.get("data", {})
    response_result["data"] = [
        {"ip": host["ip"], "plat_id": host["bk_cloud_id"], "status": host["bk_agent_alive"]} for host in hosts.values()
    ]
    return response_result


class _GseApi(object):
    MODULE = _("GSE")

    def __init__(self):
        self.get_agent_status = DataAPI(
            method="POST",
            url=GSE_APIGATEWAY_ROOT_V2 + "get_agent_status",
            module=self.MODULE,
            description=_("获取agent状态"),
            before_request=get_agent_status_before,
            after_request=get_agent_status_after,
        )


GseApi = _GseApi()
