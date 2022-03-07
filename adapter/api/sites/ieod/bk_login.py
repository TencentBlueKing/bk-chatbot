# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from adapter.api.base import DataAPI
from adapter.api.modules.utils import add_esb_info_before_request
from config.domains import USER_MANAGE_APIGATEWAY_ROOT


def get_all_user_before(params):
    params = add_esb_info_before_request(params)
    params["no_page"] = True
    params["fields"] = "username,display_name,time_zone,language"
    return params


def get_all_user_after(response_result):
    for _user in response_result.get("data", []):
        _user["chname"] = _user.pop("display_name", _user["username"])

    return response_result


def get_user_before(params):
    params = add_esb_info_before_request(params)
    params["id"] = params["bk_username"]
    return params


def get_user_after(response_result):
    if "data" in response_result:
        response_result["data"]["chname"] = response_result["data"]["display_name"]
    return response_result


class _BKLoginApi(object):
    MODULE = _("PaaS平台登录模块")

    def __init__(self):
        self.get_all_user = DataAPI(
            method="GET",
            url=USER_MANAGE_APIGATEWAY_ROOT + "list_users/",
            module=self.MODULE,
            description="获取所有用户",
            before_request=get_all_user_before,
            after_request=get_all_user_after,
            cache_time=300,
        )
        self.get_user = DataAPI(
            method="GET",
            url=USER_MANAGE_APIGATEWAY_ROOT + "retrieve_user/",
            module=self.MODULE,
            description="获取单个用户",
            before_request=get_user_before,
            after_request=get_user_after,
        )


BKLoginApi = _BKLoginApi()
