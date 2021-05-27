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
from typing import Callable, Any

from opsbot.command.argfilter import ValidateError
from opsbot.self_typing import Filter_T


class BaseValidator:
    def __init__(self, message=None):
        self.message = message

    def raise_failure(self):
        raise ValidateError(self.message)


def _raise_failure(message):
    raise ValidateError(message)


def not_empty(message=None) -> Filter_T:
    """
    Validate any object to ensure it's not empty (is None or has no elements).
    """

    def validate(value):
        if value is None:
            _raise_failure(message)
        if hasattr(value, '__len__') and value.__len__() == 0:
            _raise_failure(message)
        return value

    return validate


def fit_size(min_length: int = 0, max_length: int = None,
             message=None) -> Filter_T:
    """
    Validate any sized object to ensure the size/length
    is in a given range [min_length, max_length].
    """

    def validate(value):
        length = len(value) if value is not None else 0
        if length < min_length or \
                (max_length is not None and length > max_length):
            _raise_failure(message)
        return value

    return validate


def match_regex(pattern: str, message=None, *, flags=0,
                fullmatch: bool = False) -> Filter_T:
    """
    Validate any string object to ensure it matches a given pattern.
    """

    pattern = re.compile(pattern, flags)

    def validate(value):
        if fullmatch:
            if not re.fullmatch(pattern, value):
                _raise_failure(message)
        else:
            if not re.match(pattern, value):
                _raise_failure(message)
        return value

    return validate


def ensure_true(bool_func: Callable[[Any], bool],
                message=None) -> Filter_T:
    """
    Validate any object to ensure the result of applying
    a boolean function to it is True.
    """

    def validate(value):
        if bool_func(value) is not True:
            _raise_failure(message)
        return value

    return validate


def between_inclusive(start=None, end=None, message=None) -> Filter_T:
    """
    Validate any comparable object to ensure it's between
    `start` and `end` inclusively.
    """

    def validate(value):
        if start is not None and value < start:
            _raise_failure(message)
        if end is not None and end < value:
            _raise_failure(message)
        return value

    return validate
