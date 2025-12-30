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

from typing import Union, Callable

from opsbot.command import on_command
from opsbot.self_typing import CommandName_T


class CommandGroup:
    """
    Group a set of commands with same name prefix.
    """

    __slots__ = ('basename', 'base_kwargs')

    def __init__(self, name: Union[str, CommandName_T], **kwargs):
        self.basename = (name,) if isinstance(name, str) else name
        if 'aliases' in kwargs:
            del kwargs['aliases']  # ensure there is no aliases here
        self.base_kwargs = kwargs

    def command(self, name: Union[str, CommandName_T], **kwargs) -> Callable:
        sub_name = (name,) if isinstance(name, str) else name
        name = self.basename + sub_name

        final_kwargs = self.base_kwargs.copy()
        final_kwargs.update(kwargs)
        return on_command(name, **final_kwargs)
