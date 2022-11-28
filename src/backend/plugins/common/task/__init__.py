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
    AppTask, BKTask, parse_slots, wait_commit, real_run, validate_intent,
    Authority, Approval, Scheduler, CallbackHandler, Prediction
)
from .settings import (
    TASK_EXEC_SUCCESS, TASK_EXEC_FAIL, TASK_LIST_TIP, TASK_FINISH_TIP,
    TASK_AUTHORITY_TIP, TASK_EXEC_CANCEL
)


@on_command('bk_app_task_filter', aliases=('任务查找', '查找任务'))
async def _(session: CommandSession):
    content = f'''>**BKCHAT TIP**
            >请顺序输入任务名称，**支持模糊查询**'''
    msg_template = session.bot.send_template_msg('render_markdown_msg', content)
    task_name, _ = session.get('task_name', prompt='...', **msg_template)
    msg_template = await AppTask(session).render_app_task(task_name)
    msg_template and await session.send(**msg_template)


@on_command('bk_app_task_select')
async def _(session: CommandSession):
    try:
        app_task = session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
        app, task_id = app_task.split('|')
        session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId'] = task_id
    except (KeyError, ValueError):
        return None

    if app == 'bk_job':
        msg_template = await JobTask(session).render_job_plan_detail()
    elif app == 'bk_sops':
        msg_template = await SopsTask(session).render_sops_template_info()

    msg_template and await session.send(**msg_template)


@on_command('bk_chat_task_list', aliases=('自定义任务', '自定义技能'))
async def _(session: CommandSession):
    """
    handle api call，need to add new method to protocol
    """
    intents = await AppTask(session).describe_entity('intents', available_user=[session.ctx['msg_sender_id']],
                                                     biz_id='-1')
    if session.ctx['msg_from_type'] == 'group':
        intents = [item for item in intents if session.ctx['msg_group_id'] in item['available_group']]

    if not intents:
        await session.send('当前业务下无技能，请联系业务运维同学进行配置')
        return

    tasks = [
        {
            'id': str(intent['id']), 'text': intent['intent_name'], 'is_checked': False
        } for intent in intents[:20]
    ]
    msg_template = session.bot.send_template_msg('render_task_list_msg', 'BKCHAT', TASK_LIST_TIP,
                                                 f'请选择BKCHAT自定义技能 {TASK_FINISH_TIP}', 'bk_chat_intent_id',
                                                 tasks, 'bk_chat_task_execute')
    await session.send(**msg_template)


@on_command('bk_chat_task_execute')
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
            msg = f'识别到技能：{intent.get("intent_name")}\r\n输入 [结束] 终止会话'
            if 'timer' in intent:
                msg = f'识别到「定时」技能：{intent["timer"].get("timestamp")} 执行 ' \
                      f'{intent.get("intent_name")}\r\n输入 [结束] 终止会话'
            await session.send(msg)
            session.state['index'] = False
    else:
        try:
            intent_id = session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
            user_id = session.ctx['msg_sender_id']
        except KeyError:
            return None

        intent = (await AppTask(session).describe_entity('intents', id=int(intent_id)))[0]
        slots = await SlotRecognition(intent).fetch_slot()
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

    response = await real_run(intent, slots, user_id, session.ctx['msg_group_id'], session)
    await session.send(response.get('msg'))
    session.state.clear()


@on_command('bk_chat_task_callback', aliases=('handle_approval', 'handle_scheduler'))
async def _(session: CommandSession):
    """
    real run the cmd after deal approval and scheduler
    """
    data = await CallbackHandler(session).normalize(session.ctx.get('payload'))
    if not data:
        return

    await real_run(*data.values(), session)


@on_command('bk_chat_task_list_scheduler', aliases=('查看定时任务', '查看定时'))
async def _(session: CommandSession):
    """
    display schedulers, the you can delete old one
    """
    msg_template = await Scheduler(session, is_callback=False).list_scheduler()
    await session.send(**msg_template)


@on_command('bk_chat_task_delete_scheduler')
async def _(session: CommandSession):
    """
    delete scheduler
    """
    if session.is_first_run:
        try:
            timer_id = session.ctx['SelectedItems']['SelectedItem']['OptionIds']['OptionId']
        except KeyError:
            return None
    await Scheduler(session, is_callback=False).delete_scheduler(int(timer_id))
    await session.send('定时器删除成功')
