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

from typing import Coroutine

from opsbot import on_command, CommandSession
from opsbot import on_natural_language, NLPSession, IntentCommand
from component import fetch_intent, fetch_slot

from .api import (
    BKTask, parse_slots, wait_commit, real_run, validate_intent,
    describe_entity, Authority, Approval, Scheduler, CallbackHandler
)
from .settings import (
    TASK_EXEC_SUCCESS, TASK_EXEC_FAIL, TASK_LIST_TIP, TASK_FINISH_TIP,
    TASK_AUTHORITY_TIP, TASK_EXEC_CANCEL
)


@on_command('opsbot_trigger', aliases=('opsbot_trigger', ))
async def _(session: CommandSession):
    payload = session.ctx.get('payload')
    try:
        intent = (await describe_entity('intents', serial_number=payload.pop('intent_serial')))[0]
    except IndexError:
        return

    slots = payload.get('slots')
    user_id = payload.get('sender', 'trigger')
    group_id = payload.get('open_id')
    await real_run(intent, slots, user_id, group_id)


@on_command('opsbot_intent', aliases=('opsbot_intent', ))
async def _(session: CommandSession):
    _, biz_id, user_id = session.ctx['event_key'].split('|')
    if session.ctx['msg_sender_id'] != user_id:
        await session.send(f'{session.ctx["msg_sender_id"]} {TASK_AUTHORITY_TIP}')
        return

    if not biz_id or biz_id == '-1':
        await session.send('请绑定业务')
        return

    intents = await describe_entity('intents', biz_id=int(biz_id), available_user=[user_id])
    if session.ctx['msg_from_type'] == 'group':
        intents = [item for item in intents if session.ctx['msg_group_id'] in item['available_group']]

    if not intents:
        await session.send('当前业务下无技能，请联系业务运维同学进行配置')
        return

    rich_text = [{
        'type': 'link',
        'link': {
            'text': f'{item["intent_name"]}\n',
            'type': 'click',
            'key': f'opsbot_task|{biz_id}|{user_id}|{item["id"]}'
        }
    } for item in intents]
    rich_text.insert(0, {'text': {'content': f'{user_id} {TASK_LIST_TIP}'}, 'type': 'text'})
    rich_text.append({'text': {'content': TASK_FINISH_TIP}, 'type': 'text'})
    await session.send('', msgtype='rich_text', rich_text=rich_text)


@on_command('opsbot_task', aliases=('OPSBOT_任务执行', ))
async def task(session: CommandSession):
    if 'user_id' in session.state:
        user_id = session.state.get('user_id')
        intent = session.state.get('intent')
        slots = session.state.get('slots')
        if not slots:
            stripped_msg = session.ctx['message'].extract_plain_text().strip()
            slots = await fetch_slot(stripped_msg, intent.get('intent_id'))
            session.state['slots'] = slots
        if session.state.get('index'):
            msg = f'识别到技能：{intent.get("intent_name")}\r\n输入 [结束] 终止会话'
            if 'timer' in intent:
                msg = f'识别到「定时」技能：{intent["timer"].get("timestamp")} 执行 ' \
                      f'{intent.get("intent_name")}\r\n输入 [结束] 终止会话'
            await session.send(msg)
            session.state['index'] = False
    else:
        _, biz_id, user_id, intent_id = session.ctx['event_key'].split('|')
        if session.ctx['msg_sender_id'] != user_id:
            await session.send(f'{session.ctx["msg_sender_id"]} {TASK_AUTHORITY_TIP}')
            return

        intent = (await describe_entity('intents', id=int(intent_id)))[0]
        slots = await fetch_slot('', int(intent_id))
        if slots:
            slots[0]['prompt'] = f'{user_id} 已选择：{intent["intent_name"]}\n{slots[0]["prompt"]}'
        session.state['user_id'] = user_id
        session.state['intent'] = intent
        session.state['slots'] = slots

    is_finish = await parse_slots(slots, session)
    if not is_finish:
        return

    is_commit = wait_commit(intent, slots, session)
    if not is_commit:
        await session.send(TASK_EXEC_CANCEL)
        return

    is_approve = await getattr(Approval(session),
                               session.bot.type.title().replace('_', '')).wait_approve(intent, slots)
    if is_approve:
        return

    response = await real_run(intent, slots, user_id, session.ctx['msg_group_id'], session.bot.config.ID)
    await session.send(response.get('msg'))
    session.state.clear()


@on_command('opsbot_callback', aliases=('handle_approval', 'handle_scheduler'))
async def _(session: CommandSession):
    data = await CallbackHandler(session).normalize(session.ctx.get('payload'))
    if not data:
        return

    await real_run(*data.values(), session.bot.config.ID)


@on_command('opsbot_list_scheduler', aliases=('查看定时任务', '查看定时'))
async def _(session: CommandSession):
    msg = await Scheduler(session, is_callback=False).list_scheduler()
    await session.send('', msgtype='rich_text', rich_text=msg)


@on_command('opsbot_delete_scheduler')
async def _(session: CommandSession):
    _, timer_id = session.ctx['event_key'].split('|')
    await Scheduler(session, is_callback=False).delete_scheduler(int(timer_id))
    await session.send('定时器删除成功')


@on_natural_language
async def _(session: NLPSession):
    intent_filter = getattr(Authority(session), f'pre_{session.bot.type}')()
    if isinstance(intent_filter, Coroutine):
        intent_filter = await intent_filter
    if not intent_filter:
        return
    intents = await fetch_intent(session.msg_text.strip(), **intent_filter)
    intent = await validate_intent(intents, session)
    if not intent:
        return

    return IntentCommand(intent.get('similar', 0) * 100, 'opsbot_task',
                         args={'index': True, 'intent': intent,
                               'slots': None, 'user_id': session.ctx['msg_sender_id']})
