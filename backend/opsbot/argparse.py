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
from argparse import *

from .command import CommandSession


class ParserExit(RuntimeError):
    def __init__(self, status=0, message=None):
        self.status = status
        self.message = message


class ArgumentParser:
    """
    An ArgumentParser wrapper that avoid printing messages to
    standard I/O.
    """

    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop('session', None)
        super().__init__(*args, **kwargs)

    def _print_message(self, *args, **kwargs):
        # do nothing
        pass

    def exit(self, status=0, message=None):
        raise ParserExit(status=status, message=message)

    def parse_args(self, args=None, namespace=None):
        def finish(msg):
            if self.session and isinstance(self.session, CommandSession):
                self.session.finish(msg)

        if not args:
            finish(self.usage)
        else:
            try:
                return super().parse_args(args=args, namespace=namespace)
            except ParserExit as e:
                if e.status == 0:
                    # --help
                    finish(self.usage)
                else:
                    finish('参数不足或不正确，请使用 --help 参数查询使用帮助')
