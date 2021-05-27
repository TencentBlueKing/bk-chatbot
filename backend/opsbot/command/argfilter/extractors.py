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
from typing import List

from opsbot.message import Message
from opsbot.self_typing import Message_T


def _extract_text(arg: Message_T) -> str:
    """Extract all plain text segments from a message-like object."""
    arg_as_msg = Message(arg)
    return arg_as_msg.extract_plain_text()


def _extract_image_urls(arg: Message_T) -> List[str]:
    """
    todo adapt xwork
    Extract all image urls from a message-like object.
    """
    arg_as_msg = Message(arg)
    return [s.data['url'] for s in arg_as_msg
            if s.type == 'image' and 'url' in s.data]


def _extract_numbers(arg: Message_T) -> List[float]:
    """Extract all numbers (integers and floats) from a message-like object."""
    s = str(arg)
    return list(map(float, re.findall(r'[+-]?(\d*\.?\d+|\d+\.?\d*)', s)))


extract_text = _extract_text
extract_image_urls = _extract_image_urls
extract_numbers = _extract_numbers
