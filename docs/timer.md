# BK_CHATBOT 定时组件

## 如何使用定时插件

### 1. 确认安装依赖
```shell
pip install apscheduler
```

### 2. 系统启动默认加载
如果系统监测到已经安装 apscheduler 依赖，在后台进程启动时默认加载定时组件，观察日志
```shell
... Scheduler started
```

### 3. 系统启动默认加载
在进行插件编写的时候可以潜入定时任务逻辑
```python
# __init__.py 目录下
from opsbot import on_command, CommandSession


@on_command('begin', aliases=('开启定时'))
async def func(session: CommandSession):
    def debug_timer(tag):
        logger.info(f'timer...{tag}')
    from opsbot import scheduler
    scheduler.add_job(debug_timer, "interval", args=['debug'], seconds=10, id='my_job_id')
    await session.send('定时任务开启成功...')


@on_command('delete', aliases=('删除定时'))
async def func(session: CommandSession):
    from opsbot import scheduler
    job_ids_input, _ = session.get('job_ids_input', prompt='请输入job id')
    for job_id in job_ids_input.split('\n'):
        scheduler.remove_job(job_id)
    await session.send('定时任务删除成功...')
```

### 4. 具体操作可以查看官方文档
scheduler 是一个 APScheduler 的 AsyncIOScheduler 对象，因此关于它的更多使用方法，可以参考 [APScheduler](https://apscheduler.readthedocs.io/en/latest/userguide.html) 的官方文档
