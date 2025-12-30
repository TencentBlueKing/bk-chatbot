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

from typing import Optional, List


def _simple_chinese_to_bool(text: str) -> Optional[bool]:
    """
    Convert a chinese text to boolean.

    Examples:

        是的 -> True
        好的呀 -> True
        不要 -> False
        不用了 -> False
        你好呀 -> None
    """
    text = text.strip().lower().replace(' ', '') \
        .rstrip(',.!?~，。！？～了的呢吧呀啊呗啦')
    if text in {'要', '用', '是', '好', '对', '嗯', '行',
                'ok', 'okay', 'yeah', 'yep',
                '当真', '当然', '必须', '可以', '肯定', '没错', '确定', '确认'}:
        return True
    if text in {'不', '不要', '不用', '不是', '否', '不好', '不对', '不行', '别',
                'no', 'nono', 'nonono', 'nope', '不ok', '不可以', '不能',
                '不可以'}:
        return False
    return None


def _split_nonempty_lines(text: str) -> List[str]:
    return list(filter(lambda x: x, text.splitlines()))


def _split_nonempty_stripped_lines(text: str) -> List[str]:
    return list(filter(lambda x: x,
                       map(lambda x: x.strip(), text.splitlines())))


simple_chinese_to_bool = _simple_chinese_to_bool
split_nonempty_lines = _split_nonempty_lines
split_nonempty_stripped_lines = _split_nonempty_stripped_lines
