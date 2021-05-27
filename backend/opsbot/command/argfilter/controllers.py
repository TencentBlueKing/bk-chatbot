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
import re

from opsbot import CommandSession
from opsbot.helpers import render_expression


def handle_cancellation(session: CommandSession):
    """
    If the input is a string of cancellation word, finish the command session.
    """

    def control(value):
        if _is_cancellation(value) is True:
            session.finish(render_expression(
                session.bot.config.SESSION_CANCEL_EXPRESSION))
        return value

    return control


def _is_cancellation(sentence: str) -> bool:
    for kw in ('算', '别', '不', '停', '取消'):
        if kw in sentence:
            # a keyword matches
            break
    else:
        # no keyword matches
        return False

    if re.match(r'^那?[算别不停]\w{0,3}了?吧?$', sentence) or \
            re.match(r'^那?(?:[给帮]我)?取消了?吧?$', sentence):
        return True

    return False
