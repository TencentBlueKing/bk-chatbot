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

from collections import namedtuple

from aiocache import cached

from . import OpsBot
from .exceptions import XWorkError
from .self_typing import Context_T


PRIVATE_FRIEND = 0x0001
PRIVATE_GROUP = 0x0002
PRIVATE_DISCUSS = 0x0004
PRIVATE_OTHER = 0x0008
PRIVATE = 0x000F
DISCUSS = 0x00F0
GROUP_MEMBER = 0x0100
GROUP_ADMIN = 0x0200
GROUP_OWNER = 0x0400
GROUP = 0x0F00
SUPERUSER = 0xF000
EVERYBODY = 0xFFFF

IS_NOBODY = 0x0000
IS_PRIVATE_FRIEND = PRIVATE_FRIEND
IS_PRIVATE_GROUP = PRIVATE_GROUP
IS_PRIVATE_DISCUSS = PRIVATE_DISCUSS
IS_PRIVATE_OTHER = PRIVATE_OTHER
IS_PRIVATE = PRIVATE
IS_DISCUSS = DISCUSS
IS_GROUP_MEMBER = GROUP_MEMBER
IS_GROUP_ADMIN = GROUP_MEMBER | GROUP_ADMIN
IS_GROUP_OWNER = GROUP_ADMIN | GROUP_OWNER
IS_GROUP = GROUP
IS_SUPERUSER = 0xFFFF

_min_context_fields = (
    'Type',
    'Id',
    'Sender',
    'DeviceType',
)

_MinContext = namedtuple('MinContext', _min_context_fields)


async def check_permission(bot: OpsBot,
                           ctx: Context_T,
                           permission_required: int) -> bool:
    """
    Check if the context has the permission required.

    :param bot: OpsBot instance
    :param ctx: message context
    :param permission_required: permission required
    :return: the context has the permission
    """
    min_ctx_kwargs = {}
    for field in _min_context_fields:
        if field in ctx:
            min_ctx_kwargs[field] = ctx[field]
        else:
            min_ctx_kwargs[field] = None
    min_ctx = _MinContext(**min_ctx_kwargs)
    return await _check(bot, min_ctx, permission_required)


@cached(ttl=2 * 60)  # cache the result for 2 minute
async def _check(bot: OpsBot,
                 min_ctx: _MinContext,
                 permission_required: int) -> bool:
    permission = 0
    if min_ctx.FromUserName in bot.config.SUPERUSERS:
        permission |= IS_SUPERUSER
    else:
        permission |= IS_PRIVATE

    return bool(permission & permission_required)
