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

from adapter.api import BkMonitorApi
from blueapps.utils.logger import logger

SQL_TEMPLATE = {
    # cpu使用率
    "cpu_usage": """select
  max(usage) as value
from
  system.cpu_summary
where
  bk_biz_id = '{biz_id}'
  and bk_target_ip = '{ip}'
  and bk_target_cloud_id = '{bk_cloud_id}'
  and  time >= {start_timestamp} and time <= {end_timestamp}
group by
  minute5""",
    # CPU5分钟负载
    "cpu_load5": """select
  load5 as value
from
  system.load
where
  bk_biz_id = '{biz_id}'
  and bk_target_ip = '{ip}'
  and bk_target_cloud_id = '{bk_cloud_id}'
  and  time >= {start_timestamp} and time <= {end_timestamp}
group by
  bk_target_ip, bk_target_cloud_id""",
    # cpu单核使用率
    "cpu_detail": """select
  max(usage) as value
from
  system.cpu_detail
where
  bk_biz_id = '{biz_id}'
  and bk_target_ip = '{ip}'
  and bk_target_cloud_id = '{bk_cloud_id}'
  and  time >= {start_timestamp} and time <= {end_timestamp}
group by
  bk_target_ip, bk_target_cloud_id, device_name, minute1""",
    # 内存
    "psc_mem": """select
  max(psc_used) as value
from
  system.mem
where
  bk_biz_id = '{biz_id}'
  and bk_target_ip = '{ip}'
  and bk_target_cloud_id = '{bk_cloud_id}'
  and  time >= {start_timestamp} and time <= {end_timestamp}
group by
  minute1""",
    # 应用内存
    "mem": """select
  max(used) as value
from
  system.mem
where
  bk_biz_id = '{biz_id}'
  and bk_target_ip = '{ip}'
  and bk_target_cloud_id = '{bk_cloud_id}'
  and  time >= {start_timestamp} and time <= {end_timestamp}
group by
  minute1""",
    # 磁盘io使用率
    "disk_ioutil": """select
  max(util) as value
from
  system.io
where
  bk_biz_id = '{biz_id}'
  and bk_target_ip = '{ip}'
  and bk_target_cloud_id = '{bk_cloud_id}'
  and  time >= {start_timestamp} and time <= {end_timestamp}
group by
  bk_target_ip, bk_target_cloud_id, device_name, minute1""",
    # 磁盘空间使用率
    "disk_use": """select
  max(in_use) as value,
  mount_point as device_name
from
  system.disk
where
  bk_biz_id = '{biz_id}'
  and bk_target_ip = '{ip}'
  and bk_target_cloud_id = '{bk_cloud_id}'
  and  time >= {start_timestamp} and time <= {end_timestamp}
group by
  mount_point, minute5""",
    # 网卡入流量
    "net_speed_recv": """select
  max(speed_recv) as value
from
  system.net
where
  bk_biz_id = '{biz_id}'
  and bk_target_ip = '{ip}'
  and bk_target_cloud_id = '{bk_cloud_id}'
  and  time >= {start_timestamp} and time <= {end_timestamp}
group by
  bk_target_ip, bk_target_cloud_id, device_name, minute5""",
    # 网卡入包量
    "net_speed_packets_recv": """select
  max(speed_packets_recv) as value
from
  system.net
where
  bk_biz_id = '{biz_id}'
  and bk_target_ip = '{ip}'
  and bk_target_cloud_id = '{bk_cloud_id}'
  and  time >= {start_timestamp} and time <= {end_timestamp}
group by
  bk_target_ip, bk_target_cloud_id, device_name, minute5""",
    # 网卡出流量
    "net_speed_sent": """select
  max(speed_sent) as value
from
  system.net
where
  bk_biz_id = '{biz_id}'
  and bk_target_ip = '{ip}'
  and bk_target_cloud_id = '{bk_cloud_id}'
  and  time >= {start_timestamp} and time <= {end_timestamp}
group by
  bk_target_ip, bk_target_cloud_id, device_name, minute5""",
    # 网卡出包量
    "net_speed_packets_sent": """select
  max(speed_packets_sent) as value
from
  system.net
where
  bk_biz_id = '{biz_id}'
  and bk_target_ip = '{ip}'
  and bk_target_cloud_id = '{bk_cloud_id}'
  and  time >= {start_timestamp} and time <= {end_timestamp}
group by
  bk_target_ip, bk_target_cloud_id, device_name, minute5""",
}


def make_sql(name, **kwargs):
    """sql生成器"""
    metric_sql = SQL_TEMPLATE.get(name)
    return metric_sql.format(**kwargs)


class BkMonitor:
    """
    监控接口
    """

    @classmethod
    def get_ts_data(cls, bk_username, metric_name, **kwargs):
        """
        指标信息查询
        """
        sql = make_sql(metric_name, **kwargs)

        kwargs_tsquery = {
            "bk_username": bk_username,
            "sql": sql,
        }

        try:
            res = BkMonitorApi.get_ts_data(kwargs_tsquery)

            if metric_name in [
                "cpu_detail",
                "disk_ioutil",
                "net_speed_recv",
                "net_speed_packets_recv",
                "net_speed_sent",
                "net_speed_packets_sent",
                "disk_use",
            ]:
                res["list"] = [
                    {"time": d["time"], "value": d["value"], "dimension": d["device_name"]}
                    for d in res["list"]
                    if d["device_name"] and d["value"] is not None
                ]
                res["dimensions"] = list({d["dimension"] for d in res["list"]})

            return res
        except Exception as e: # pylint: disable=broad-except
            logger.error(f"[API]get_metric_data error {e}")

        return None
