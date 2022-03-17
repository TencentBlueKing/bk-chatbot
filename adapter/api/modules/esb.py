# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from config.domains import ESB_APIGATEWAY_ROOT_V2
from ..base import DataAPI, BaseApi


def add_params_before_request(params):
    params["bk_app_code"] = settings.APP_CODE
    params["bk_app_secret"] = settings.SECRET_KEY
    params["bk_username"] = "admin"
    return params


class _ESBApi(BaseApi):

    MODULE = _("ESB")

    def __init__(self):
        self.get_api_public_key = DataAPI(
            method="POST",
            url=ESB_APIGATEWAY_ROOT_V2 + "get_api_public_key",
            module=self.MODULE,
            description="get api public key",
            default_return_value=None,
            before_request=add_params_before_request,
            after_request=None,
        )


ESBApi = _ESBApi()
