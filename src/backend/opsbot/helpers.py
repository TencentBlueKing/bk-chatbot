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

import hashlib
import random
from typing import Sequence, Callable, Any

from .adapter import Bot
from .exceptions import Error
from .stdlib import escape
from .self_typing import Context_T, Message_T, Expression_T


def context_id(ctx: Context_T, *,
               mode: str = 'default',
               use_hash: bool = False) -> str:
    """
    Calculate a unique id representing the current context.

    mode:
      default: one id for one context
      group: one id for one group or discuss
      user: one id for one user

    :param ctx: the context dict
    :param mode: unique id mode: "default", "group", or "user"
    :param use_hash: use md5 to hash the id or not
    """
    ctx_id = f'/{ctx["msg_from_type"]}/{ctx["msg_group_id"]}/{ctx["msg_sender_id"]}'
    if ctx_id and use_hash:
        ctx_id = hashlib.md5(ctx_id.encode('ascii')).hexdigest()
    return ctx_id


async def send(bot: Bot, ctx: Context_T,
               message: Message_T, *,
               ensure_private: bool = False,
               ignore_failure: bool = True,
               **kwargs) -> Any:
    """Send a message ignoring failure by default."""
    try:
        if ensure_private:
            ctx = ctx.copy()
            ctx['msg_from_type'] = 'single'
        return await bot.send(ctx, message, **kwargs)
    except Error:
        if not ignore_failure:
            raise
        return None


def render_expression(expr: Expression_T, *args,
                      escape_args: bool = True, **kwargs) -> str:
    """
    Render an expression to message string.

    :param expr: expression to render
    :param escape_args: should escape arguments or not
    :param args: positional arguments used in str.format()
    :param kwargs: keyword arguments used in str.format()
    :return: the rendered message
    """
    if isinstance(expr, Callable):
        expr = expr(*args, **kwargs)
    elif isinstance(expr, Sequence) and not isinstance(expr, str):
        expr = random.choice(expr)
    if escape_args:
        for k, v in kwargs.items():
            if isinstance(v, str):
                kwargs[k] = escape(v)
    return expr.format(*args, **kwargs)
