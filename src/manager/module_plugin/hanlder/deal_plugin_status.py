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


from blueapps.utils.logger import logger

from common.design.strategy import Strategy
from common.redis import RedisClient
from src.manager.handler.api.bk_itsm import BkITSM
from src.manager.module_plugin.hanlder.api import PluginManage
from src.manager.module_plugin.constants import (
    PLUGIN_ITSM_CALLBACK_URI,
    PLUGIN_ITSM_SERVICE_ID,
    PROD_BOT_NAME,
    PROD_PLUGIN_URI_ENV,
    STAG_BOT_NAME,
    STAG_PLUGIN_URI_ENV,
)
from src.manager.module_plugin.models import Plugin, PluginAuditLog


class DealPluginStatus(Strategy):
    _map = dict()

    @classmethod
    def do(cls, obj: Plugin, new_status: int, old_status: int):
        """
        更新状态
        """
        return cls._map.value[new_status](obj, old_status)


def get_plugin_params(obj: Plugin) -> dict:
    """
    获取插件参数
    @param obj:
    @return:
    """
    params = {
        "key": obj.plugin_key,
        "name": obj.plugin_name,
        "addr": obj.plugin_addr,
        "choose_biz": obj.choose_biz,
        "start": obj.plugin_start if obj.plugin_start else obj.actions[0].get("key"),
        "web": obj.plugin_web,
        "tag": obj.plugin_tag,
        "status": 1,
        "global": obj.plugin_global,
        "actions": obj.actions,
        "wait_time": obj.plugin_wait_time,
    }
    return params


@DealPluginStatus.register(Plugin.PluginStatus.DEFAULT.value)
def cancel_stag_plug(obj: Plugin, old_status: int):
    """
    取消预发布
    @param obj:
    @param old_status:
    @return:
    """
    if old_status not in [Plugin.PluginStatus.STAG.value]:
        raise ValueError("插件状态不为预发布状态")
    plugin_manage = PluginManage(STAG_PLUGIN_URI_ENV)
    plugin_manage.del_service(obj.plugin_key)


@DealPluginStatus.register(Plugin.PluginStatus.STAG.value)
def release_stag_plugin(obj: Plugin, old_status: int):
    """
    预发布插件: 0/1 状态才能预发布
    @return:
    """

    # 判断旧状态是否在0和1状态
    if old_status not in [Plugin.PluginStatus.DEFAULT.value, Plugin.PluginStatus.STAG.value]:
        raise ValueError("插件状态不为创建或者预发布状态")

    # 添加到预发布环境
    params = get_plugin_params(obj)
    plugin_manage = PluginManage(STAG_PLUGIN_URI_ENV)
    plugin_manage.add_service(**params)
    plugin_manage.reload(STAG_BOT_NAME)  # 重启测试环境机器人
    return


@DealPluginStatus.register(Plugin.PluginStatus.AUDIT.value)
def audit_plugin(obj: Plugin, old_status: int):
    """
    审核: 预发布 ==> 审核状态
    @return:
    """
    if old_status not in [Plugin.PluginStatus.STAG.value]:
        raise ValueError("插件状态不为预发布状态")

    params = {
        "service_id": PLUGIN_ITSM_SERVICE_ID,
        "creator": obj.updated_by,
        "fields": [
            {"key": "title", "value": f"插件[{obj.plugin_name}]权限申请"},
            {"key": "plugin_name", "value": obj.plugin_name},
            {"key": "take_effect", "value": "全部业务" if len(obj.biz_list) == 0 else "部分业务"},
            {"key": "creator", "value": obj.updated_by},
            {"key": "plugin_desc", "value": obj.plugin_desc},
        ],
        "meta": {
            "callback_url": PLUGIN_ITSM_CALLBACK_URI,
        },
    }

    # 内置CD
    redis_client = RedisClient()
    if not redis_client.set_nx(f"plugin_audit_{obj.id}", "cd", 10):
        raise Exception("请10秒后再次尝试上架需求")

    # itsm 提单
    ret = BkITSM.create_ticket(**params)
    logger.info(ret)
    result = ret.get("result", False)
    if not result:
        raise Exception("itsm添加错误审核单据错误")
    sn = ret.get("data", {}).get("sn")
    if not sn:
        raise Exception("itsm返回异常sn为空")
    plugin_audit_log = PluginAuditLog.objects.create(plugin_id=obj.id, sn=sn, plugin_username=obj.updated_by)
    return plugin_audit_log


@DealPluginStatus.register(Plugin.PluginStatus.ADDED.value)
def release_prod_plugin(obj: Plugin, old_status: int):
    """
    正式发布插件
    @return:
    """
    if old_status not in [Plugin.PluginStatus.AUDIT.value]:
        raise ValueError("插件状态不为审核状态")

    # 数据添加
    params = get_plugin_params(obj)
    plugin_manage = PluginManage(PROD_PLUGIN_URI_ENV)
    rsp = plugin_manage.add_service(**params)
    plugin_manage.reload(PROD_BOT_NAME)  # 重启正式环境机器人

    return rsp


@DealPluginStatus.register(Plugin.PluginStatus.SOLD_OUT.value)
def sold_out_prod_plugin(obj: Plugin, old_status: int):
    """
    下架==>回滚到预发布状态
    @return:
    """

    if old_status not in [Plugin.PluginStatus.ADDED.value]:
        raise ValueError("插件上架不为上架状态")

    # 插件删除
    plugin_manage = PluginManage(PROD_PLUGIN_URI_ENV)
    plugin_manage.del_service(obj.plugin_key)

    # 状态修改
    obj.plugin_status = Plugin.PluginStatus.STAG.value
    obj.save()


@DealPluginStatus.register(Plugin.PluginStatus.CANCEL_AUDIT.value)
def cancel_audit_plugin(obj: Plugin, old_status: int):
    """
    取消审核 ==> 预发布状态
    @return:
    """
    if old_status not in [Plugin.PluginStatus.AUDIT.value]:
        raise ValueError("插件状态不为审核状态")

    # 状态修改
    obj.plugin_status = Plugin.PluginStatus.STAG.value
    obj.save()


def del_stag_plugin(obj: Plugin):
    """
    删除预发布插件
    """
    plugin_manage = PluginManage(STAG_PLUGIN_URI_ENV)
    plugin_manage.del_service(obj.plugin_key)


def deal_audit_plugin(plugin_id: int, ok: bool):
    """
    审核插件: 审核状态==>上架状态
    """
    plugin_obj: Plugin = Plugin.objects.get(pk=plugin_id)

    # 判断是否审核状态
    if plugin_obj.plugin_status == Plugin.PluginStatus.AUDIT.value:
        status = Plugin.PluginStatus.STAG.value  # 默认给预发布状态
        # 通过到上架状态，不通过回滚到预发布状态
        if ok:
            # 发布到正式环境中
            added_status = Plugin.PluginStatus.ADDED.value  # 上架状态
            ret = DealPluginStatus.do(plugin_obj, added_status, plugin_obj.plugin_status)
            status = added_status if ret.get("result") else status
        plugin_obj.plugin_status = status
        plugin_obj.save()
