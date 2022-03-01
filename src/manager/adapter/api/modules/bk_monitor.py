from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from adapter.api.base import DataAPI
from config.domains import MONITOR_APIGATEWAY_ROOT


def add_params_before_request(params):
    params["bk_app_code"] = settings.APP_CODE
    params["bk_app_secret"] = settings.SECRET_KEY
    params["bk_username"] = params.get("bk_username", "admin")
    return params


class _BkMonitorApi:
    MODULE = _("BKMONITOR")

    @property
    def get_ts_data(self):
        return DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "get_ts_data",
            description=_("查询时序数据"),
            module=self.MODULE,
            before_request=add_params_before_request,
        )


BkMonitorApi = _BkMonitorApi()