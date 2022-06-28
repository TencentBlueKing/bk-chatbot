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

    @property
    def save_action_config(self):
        return DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "save_action_config",
            description=_("保存处理套餐"),
            module=self.MODULE,
        )

    @property
    def edit_action_config(self):
        return DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "edit_action_config",
            description=_("编辑处理套餐"),
            module=self.MODULE,
        )

    @property
    def delete_action_config(self):
        return DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "delete_action_config",
            description=_("删除处理套餐"),
            module=self.MODULE,
        )

    @property
    def search_alarm_strategy(self):
        return DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "search_alarm_strategy",
            description=_("查询告警策略"),
            module=self.MODULE,
        )

    @property
    def search_alarm_strategy_v2(self):
        return DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "search_alarm_strategy_v2",
            description=_("查询告警策略V2"),
            module=self.MODULE,
        )

    @property
    def search_alarm_strategy_v3(self):
        return DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "search_alarm_strategy_v3",
            description=_("查询告警策略V3"),
            module=self.MODULE,
        )

    @property
    def update_partial_strategy_v3(self):
        return DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "update_partial_strategy_v3",
            description=_("批量更新策略局部配置"),
            module=self.MODULE,
        )


BkMonitorApi = _BkMonitorApi()
