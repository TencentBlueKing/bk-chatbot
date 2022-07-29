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


import datetime


def get_time(text):
    """
    获取时间
    :param text:
    :return:
    """
    timestamp = datetime.datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
    utc_timestamp = timestamp + datetime.timedelta(hours=8)
    str_time = utc_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return str_time


class OriginalAlarm:
    """
    原始告警
    """

    def __init__(self, info):
        """
        初始化数据
        @param info:
        """
        self.info = info  # 基础信息
        self.bk_biz_name = None  # 业务名称
        self.event_level_name = None  # 告警等级名称
        self.begin_time = None  # 开始时间
        self.create_time = None  # 告警出来的时间
        self.anomaly_message = None  # 告警消息
        self.origin_alarm_value = None  # 告警异常值`
        self.alarm_dimension = ""  # 告警维度
        self.relation_info = None  # 相关消息
        self.all_dimensions = None  # 全部维度
        self.dimensions = None
        self.bk_target_ip = None  # 告警目标IP
        self.bk_target_cloud_id = None  # 云区域
        self.device_name = None  # 设备名称
        self.get_base_info()  # 初始化数据

    def get_base_info(self):
        """
        获取基础信息
        @return:
        """
        self.bk_biz_name = self.info.get("bk_biz_name")  # 告警业务
        self.get_event_info()
        self.get_anomaly_info()

    def get_event_info(self):
        """
        获取事件相关的信息
        @return:
        """
        event = self.info.get("event")  # 告警事件
        self.event_level_name = event.get("level_name")  # 告警级别
        self.begin_time = get_time(event.get("begin_time"))  # 首次异常

    def get_anomaly_info(self):
        """
        获取异常相关的信息
        @return:
        """
        latest_anomaly_record = self.info.get("latest_anomaly_record")
        self.create_time = get_time(latest_anomaly_record.get("create_time"))  # 最近异常时间
        origin_alarm = latest_anomaly_record.get("origin_alarm")
        # 异常消息
        self.anomaly_message = "".join(
            [f"{v.get('anomaly_message')}" for k, v in origin_alarm.get("anomaly", {}).items()]
        )
        # 异常告警信息的data
        origin_alarm_data = origin_alarm.get("data", {})  # 异常数据
        self.origin_alarm_value = origin_alarm_data.get("value")  # 异常值
        # 异常维度信息
        dimension_translation = origin_alarm.get("dimension_translation", {})
        bk_topo_node = dimension_translation.get("bk_topo_node", {})  # 业务topo
        bk_topo_node_display_value = bk_topo_node.get("display_value", [])

        # 相关信息
        relation_info = self.info.get("related_info")
        self.relation_info = (
            relation_info
            if relation_info
            else ",".join(
                list(
                    map(
                        lambda x: f"{x.get('bk_obj_name')}({x.get('bk_inst_name')})",
                        bk_topo_node_display_value,
                    )
                )
            )
        )

        # 云区域
        self.bk_target_cloud_id = dimension_translation.get("bk_target_cloud_id", {}).get("value")
        # 目标IP
        self.bk_target_ip = dimension_translation.get("bk_target_ip", {}).get("value")
        # 设备名称
        self.device_name = dimension_translation.get("device_name", {}).get("value")
        # 告警维度
        if self.bk_target_cloud_id:
            self.alarm_dimension += f"云区域ID={self.bk_target_cloud_id}"
        if self.bk_target_ip:
            self.alarm_dimension += f",目标IP={self.bk_target_ip}"
        if self.device_name:
            self.alarm_dimension += f",设备名={self.device_name}"
        # 全部维度
        self.dimensions = origin_alarm.get("dimensions", {})

    def get_markdown(self):
        """
        获取markdown
        @return:
        """
        self.all_dimensions = "\n                    ".join(
            [f"{k} = {v}" for k, v in self.dimensions.items()],
        )
        content = f"""`告警级别:` {self.event_level_name}
`首次异常:` {self.begin_time}
`最近异常:` {self.create_time}
`告警内容:` {self.anomaly_message}
`当前数值:` {self.origin_alarm_value}
`告警业务:` {self.bk_biz_name}
`告警目标:` {self.bk_target_ip}
`告警维度:` {self.alarm_dimension}
`关联信息:` {self.relation_info}
`全部维度:` {self.all_dimensions}"""
        return content

    def get_text(self):
        """

        @return:
        """
        self.all_dimensions = "\n                    ".join(
            [f"{k} = {v}" for k, v in self.dimensions.items()],
        )
        content = f"""告警级别: {self.event_level_name}
首次异常: {self.begin_time}
最近异常: {self.create_time}
告警内容: {self.anomaly_message}
当前数值: {self.origin_alarm_value}
告警业务: {self.bk_biz_name}
告警目标: {self.bk_target_ip}
告警维度: {self.alarm_dimension}
关联信息: {self.relation_info}
全部维度: {self.all_dimensions}
        """
        return content

    def wework_bot(self):
        """
        wework_bot
        @return:
        """
        params = {
            "msg_type": "markdown",
            "msg_param": {"content": self.get_markdown()},
        }
        return params

    def wework(self):
        """
        wework
        @return:
        """
        params = {
            "msg_type": "markdown",
            "msg_param": {"content": self.get_markdown()},
        }
        return params

    def slack(self):
        """
        @return:
        """
        content = self.get_text()
        params = {
            "msg_type": "text",
            "msg_param": {"text": content},
        }
        return params
