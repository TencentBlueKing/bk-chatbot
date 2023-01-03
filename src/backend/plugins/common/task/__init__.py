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
from component import SlotRecognition
from plugins.common.job import JobTask
from plugins.common.sops import SopsTask

from .api import (
    AppTask, BKTask, parse_slots, wait_commit,
    real_run, validate_intent, Authority, Approval,
    Scheduler, CallbackHandler, Prediction
)
from .settings import (
    TASK_FILTER_KEY, TASK_FILTER_ALIAS, TASK_FILTER_SELECT_KEY,
    TASK_EXEC_SUCCESS, TASK_EXEC_FAIL, TASK_LIST_TIP,
    TASK_FINISH_TIP, TASK_AUTHORITY_TIP, TASK_EXEC_CANCEL,
    TASK_LIST_KEY, TASK_LIST_ALIAS, TASK_EXECUTE_KEY,
    TASK_CALLBACK_KEY, TASK_CALLBACK_ALIAS, TASK_LIST_SCHEDULER_KEY,
    TASK_LIST_SCHEDULER_ALIAS, TASK_DEL_SCHEDULER_KEY,
    TASK_FILTER_QUERY_PREFIX, TASK_FILTER_QUERY_TIP,
    TASK_LIST_NULL_MSG, TASK_SKILL_SELECT_TIP, TASK_SKILL_RECOGNIZE_TIP,
    TASK_SKILL_SCHEDULER_TIP, TASK_SKILL_SELECTED_PROMPT,
    TASK_DEL_SCHEDULER_SUCCESS_MSG
)


@on_command(TASK_FILTER_KEY, aliases=TASK_FILTER_ALIAS)
async def _(session: CommandSession):
    title = '<bold>BKCHAT TIP<bold>'
    content = f'{TASK_FILTER_QUERY_PREFIX}，<bold>{TASK_FILTER_QUERY_TIP}<bold>'
    msg_template = session.bot.send_template_msg('render_markdown_msg', title, content)
    task_name, _ = session.get('task_name', prompt='...', **msg_template)
    msg_template = await AppTask(session).render_app_task(task_name)
    msg_template and await session.send(**msg_template)


@on_command(TASK_FILTER_SELECT_KEY)
async def _(session: CommandSession):
    try:
        app_task = session.bot.parse_action('parse_select', session.ctx)
        app, task_id = app_task.split('|')
        session.bot.parse_action('update_select', session.ctx, task_id)
    except (KeyError, ValueError):
        return None

    if app == 'bk_job':
        msg_template = await JobTask(session).render_job_plan_detail()
    elif app == 'bk_sops':
        msg_template = await SopsTask(session).render_sops_template_info()

    msg_template and await session.send(**msg_template)


@on_command(TASK_LIST_KEY, aliases=TASK_LIST_ALIAS)
async def _(session: CommandSession):
    """
    handle api call，need to add new method to protocol
    """
    intents = await AppTask(session).describe_entity('intents', available_user=[session.ctx['msg_sender_id']],
                                                     biz_id='-1')
    if session.ctx['msg_from_type'] == 'group':
        intents = [item for item in intents if session.ctx['msg_group_id'] in item['available_group']]

    if not intents:
        await session.send(TASK_LIST_NULL_MSG)
        return

    msg_template = session.bot.send_template_msg('render_task_list_msg',
                                                 'BKCHAT',
                                                 TASK_LIST_TIP,
                                                 f'{TASK_SKILL_SELECT_TIP} {TASK_FINISH_TIP}',
                                                 'bk_chat_intent_id',
                                                 intents,
                                                 'bk_chat_task_execute',
                                                 render=lambda x: {'id': str(x['id']),
                                                                   'text': x['intent_name'],
                                                                   'is_checked': False})
    await session.send(**msg_template)


@on_command(TASK_EXECUTE_KEY)
async def task(session: CommandSession):
    """
    support user intent config，combined with nlp/nlu，
    recognize user meaning and transfer it to the bk platform task
    """
    if 'user_id' in session.state:
        user_id = session.state.get('user_id')
        intent = session.state.get('intent')
        slots = session.state.get('slots')
        if not slots:
            stripped_msg = session.ctx['message'].extract_plain_text().strip()
            slots = await SlotRecognition(intent).fetch_slot(stripped_msg)
            session.state['slots'] = slots
        if session.state.get('index'):
            msg = TASK_SKILL_RECOGNIZE_TIP.format(intent.get("intent_name"))
            if 'timer' in intent:
                msg = TASK_SKILL_SCHEDULER_TIP.format(intent["timer"].get("timestamp"),
                                                      intent.get("intent_name"))
            await session.send(msg)
            session.state['index'] = False
    else:
        intent_id = session.bot.parse_action('parse_select', session.ctx)
        if not intent_id:
            return None
        user_id = session.ctx['msg_sender_id']
        intent = (await AppTask(session).describe_entity('intents', id=int(intent_id)))[0]
        slots = await SlotRecognition(intent).fetch_slot()
        if slots:
            slots[0]['prompt'] = TASK_SKILL_SELECTED_PROMPT.format(user_id, intent["intent_name"],
                                                                   slots[0]["prompt"])
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

    response = await real_run(intent, slots, user_id, session.ctx['msg_group_id'], session)
    await session.send(response.get('msg'))
    session.state.clear()


@on_command(TASK_CALLBACK_KEY, aliases=TASK_CALLBACK_ALIAS)
async def _(session: CommandSession):
    """
    real run the cmd after deal approval and scheduler
    """
    data = await CallbackHandler(session).normalize(session.ctx.get('payload'))
    if not data:
        return

    await real_run(*data.values(), session)


@on_command(TASK_LIST_SCHEDULER_KEY, aliases=TASK_LIST_SCHEDULER_ALIAS)
async def _(session: CommandSession):
    """
    display schedulers, the you can delete old one
    """
    msg_template = await Scheduler(session, is_callback=False).list_scheduler()
    await session.send(**msg_template)


@on_command(TASK_DEL_SCHEDULER_KEY)
async def _(session: CommandSession):
    """
    delete scheduler
    """
    if session.is_first_run:
        timer_id = session.bot.parse_action('parse_select', session.ctx)
        if not timer_id:
            return
    await Scheduler(session, is_callback=False).delete_scheduler(int(timer_id))
    await session.send(TASK_DEL_SCHEDULER_SUCCESS_MSG)
