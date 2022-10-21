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


class OriginalBroadcast:
    """
    原始播报数据
    """

    def __init__(self, parse_result, **kwargs):
        """
        初始化数据
        """
        self.parse_result = parse_result
        self.text_content = ""
        self.markdown_content = ""
        self.mini_program_content = ""

        self.init_markdown()
        self.init_text()
        self.init_mini_program()

    @staticmethod
    def _format_time(total_seconds):
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        if days:
            return f"{int(days)}天{int(hours)}时{int(minutes)}分{int(seconds)}秒"
        if hours:
            return f"{int(hours)}时{int(minutes)}分{int(seconds)}秒"
        if minutes:
            return f"{int(minutes)}分{int(seconds)}秒"
        if seconds:
            return f"{int(seconds)}秒"

        return "--"

    def init_markdown(self, task_name_link=False):
        step_data = self.parse_result.get("step_data", [])
        else_executing_step_list = self.parse_result.get("else_executing_step_list", [])
        step_line_list = []
        else_executing_line_list = []
        for step in step_data:
            step_status_str = f"""<font color=\"{step.get("step_status_color")}\">{step.get("step_status")}</font>"""
            step_line = " Step{} [{}] {}".format(step["step_index"], step_status_str, step["step_name"])
            if step["start_time"]:
                step_line += " [开始时间:{} 耗时{}]".format(step["start_time"], self._format_time(step["step_duration"]))

            if step["step_status"] == "执行中":
                step_line = step_line.strip(" ")
                step_line = f" **{step_line}**"

            step_line_list.append(step_line)

        for step in else_executing_step_list:
            step_status_str = f"""<font color=\"{step.get("step_status_color")}\">{step.get("step_status")}</font>"""
            step_line = "Step{} [{}] {}".format(step["step_index"], step_status_str, step["step_name"])
            if step["start_time"]:
                step_line += " [开始时间:{} 耗时{}]".format(step["start_time"], self._format_time(step["step_duration"]))

            step_line = f" **{step_line}**"
            else_executing_line_list.append(step_line)

        step_line_list_str = "\n".join(step_line_list)
        else_executing_line_list_str = "\n".join(else_executing_line_list)
        task_start_time = self.parse_result.get("start_time")
        task_exec_time = "开始时间:-- 耗时--"
        if task_start_time:
            task_exec_time = "[开始时间:{} 耗时{}]".format(
                task_start_time, self._format_time(self.parse_result.get("task_duration"))
            )
        step_schedule = "{}/{}".format(
            self.parse_result.get("current_step_num"), self.parse_result.get("total_step_num")
        )
        if task_name_link:
            task_name = f"[{self.parse_result.get('task_name')}]({self.parse_result.get('task_url')})"
        else:
            task_name = self.parse_result.get("task_name")
        self.markdown_content = (
            f""" **任务实时播报如下:**
 **任务名:** {task_name}
 **执行时间:** {task_exec_time}
 **执行状态:** <font color=\"{self.parse_result.get("task_status_color")}\">{self.parse_result.get("task_status")}</font>"""
            f"""({step_schedule})
{step_line_list_str}"""
        )
        if else_executing_step_list:
            self.markdown_content = f"""{self.markdown_content}
 ...
{else_executing_line_list_str}"""

    def init_text(self):
        step_data = self.parse_result.get("step_data", [])
        else_executing_step_list = self.parse_result.get("else_executing_step_list", [])
        step_line_list = []
        else_executing_line_list = []
        for step in step_data:
            step_line = " Step{} [{}] {}".format(step["step_index"], step["step_status"], step["step_name"])
            if step["start_time"]:
                step_line += " [开始时间:{} 耗时{}]".format(step["start_time"], self._format_time(step["step_duration"]))

            step_line_list.append(step_line)

        for step in else_executing_step_list:
            step_line = " Step{} [{}] {}".format(step["step_index"], step["step_status"], step["step_name"])
            if step["start_time"]:
                step_line += " [开始时间:{} 耗时{}]".format(step["start_time"], self._format_time(step["step_duration"]))

            else_executing_line_list.append(step_line)

        step_line_list_str = "\n".join(step_line_list)
        else_executing_line_list_str = "\n".join(else_executing_line_list)
        task_start_time = self.parse_result.get("start_time")
        task_exec_time = "开始时间:-- 耗时--"
        if task_start_time:
            task_exec_time = "[开始时间:{} 耗时{}]".format(
                task_start_time, self._format_time(self.parse_result.get("task_duration"))
            )
        step_schedule = "{}/{}".format(
            self.parse_result.get("current_step_num"), self.parse_result.get("total_step_num")
        )
        self.text_content = f""" 任务实时播报如下:
 任务名: {self.parse_result.get("task_name")}
 执行时间: {task_exec_time}
 执行状态: [{self.parse_result.get("task_status")}]({step_schedule})
{step_line_list_str}"""

        if else_executing_line_list:
            self.text_content = f"""{self.text_content}
 ...
{else_executing_line_list_str}"""

    def init_mini_program(self):
        self.mini_program_content = ""

    @property
    def wework_bot(self):
        """
        wework_bot
        @return:
        """
        self.init_markdown()
        return "markdown", self.markdown_content

    @property
    def wework(self):
        """
        wework
        @return:
        """
        self.init_markdown(task_name_link=True)
        return "markdown", self.markdown_content

    @property
    def slack(self):
        """
        @return:
        """
        return "text", self.text_content

    @property
    def slack_webhook(self):
        """
        @return:
        """
        return "text", self.text_content

    @property
    def qq(self):
        """
        qq发送
        @return:
        """
        return "text", self.text_content

    @property
    def mini_program(self):
        """
        微信小程序
        @return:
        """
        return "text", self.text_content

    @property
    def lark_webhook(self):
        """
        飞书 webhook
        @return:
        """

        return "text", self.text_content

    @property
    def ding_webhook(self):
        return "text", self.text_content
