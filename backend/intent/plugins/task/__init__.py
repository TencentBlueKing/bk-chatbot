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

from opsbot import on_command, CommandSession
from opsbot import on_natural_language, NLPSession, IntentCommand
from opsbot.log import logger
from opsbot.helpers import render_expression
from component import fetch_intent, fetch_slot, RedisClient

from .api import BKTask, parse_slots, wait_commit, summary_statement
from .settings import EXPR_DONT_UNDERSTAND, TASK_EXEC_SUCCESS, TASK_EXEC_FAIL


@on_command('opsbot_task', aliases=('OPSBOT_任务执行'))
async def task(session: CommandSession):
    user_id = session.state.get('user_id')

    slots = session.state.get('slots')
    is_finish = await parse_slots(slots, session)
    if not is_finish:
        return

    intent = session.state.get('intent')
    is_commit = wait_commit(intent, slots, session)
    if not is_commit:
        return

    try:
        await BKTask(intent, slots, user_id).run()
        msg = summary_statement(intent, slots, TASK_EXEC_SUCCESS)
    except Exception as e:
        msg = TASK_EXEC_FAIL
        logger.error(f'{msg} {intent.get("intent_name")}, error: {e}')
        logger.exception(e)

    await session.send(msg)
    session.state.clear()


@on_natural_language
async def _(session: NLPSession):
    if session.bot.type == 'in_xwork':
        if session.ctx['msg_from_type'] == 'single':
            await session.send('暂不支持单聊')
            return

        biz_id = RedisClient(env="prod").hash_get("chat_group_biz", session.ctx['msg_group_id'])
        if not biz_id or str(biz_id) == '-1':
            return

        r = await session.bot.call_action('tencent/user/convert_to_name',
                                          userid_list=[session.ctx['msg_sender_id']])
        user_id = r.get('user_list')[0]['name'] if r.get('user_list') else ''
    else:
        biz_id = None
        user_id = session.ctx['msg_sender_id']

    stripped_msg = session.msg_text.strip()
    intents = await fetch_intent(stripped_msg, biz_id=int(biz_id), user_id=user_id)
    if not intents:
        await session.send(render_expression(EXPR_DONT_UNDERSTAND))
        return

    intent = intents[0]
    if not intent.get('status'):
        await session.send(render_expression('该技能未开启'))
        return

    await session.send(f'识别到技能：{intent.get("intent_name")}\r\n输入 [结束] 终止会话')
    slots = await fetch_slot(stripped_msg, intent.get('intent_id'))

    return IntentCommand(intent.get('similar', 0) * 100,
                         'opsbot_task',
                         args={
                             'intent': intent,
                             'slots': slots,
                             'user_id': user_id,
                             'group_id': session.ctx['msg_group_id']
                        })
