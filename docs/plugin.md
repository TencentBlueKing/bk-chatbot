# BK_CHATBOT 插件开发文档

## 如何制作机器人插件

### 1. 创建插件目录

> linux环境下执行

```shell
# 创建
cd bk-chatbot/src/backend || exit
sh control create_plugin common demo_plugin

# 查看插件目录
cd bk-chatbot/src/backend/plugins/
ls -l demo_plugin
```

> 插件目录结构

```shell
├── demo_plugin                 # 插件名称
│   ├── __init__.py             # 路由配置
│   ├── api.py                  # api存放
│   ├── settings.py             # 配置
│   └── stdlib.py               # 算法等逻辑
```

### 2. 编写插件

> 编写插件回复消息
```python
# __init__.py 目录下
from opsbot import on_command, CommandSession

"""
on_command 装饰器将函数声明为一个命令处理器
这里 demo 为命令的名字，同时允许使用别名「第一个插件」「测试插件」
"""

@on_command('demo', aliases=('第一个插件', '测试插件'))
async def func(session: CommandSession):
    # 通过IM发送消息给
    await session.send('收到')
```

> 编写插件获取参数
```python
# __init__.py 目录下
from opsbot import on_command, CommandSession


@on_command('reboot', aliases=('重启服务器'))
async def func(session: CommandSession):
    # 取得消息的内容，并且去掉首尾的空白符
    server = session.current_arg_text.strip()
    while not server:
        # 获取用户参数
        server = (await session.get(prompt='你想重启那个服务器？')).strip()
    await session.send(f'重启服务器{server}...')
```

### 3.「业务信息查询」插件开发

> 可能不是最优实践，只为说明问题
> 配置信息
```python
# settings 目录下
TOP_RANK = 3
PARSE_RATE = 0.6
```

> 路由及核心处理逻辑
```python
# __init__.py 目录下
import json

from opsbot import on_command, CommandSession
from .api import search_biz
from .stdlib import parse_biz


@on_command('search_biz', aliases=('业务查询'))
async def func(session: CommandSession):
    # 获取参数名
    input_biz_name = session.current_arg_text.strip()
    while not input_biz_name:
        input_biz_name = (await session.get(prompt='你想查询哪个业务？')).strip()
    # 调用解析函数
    real_biz_name = await self.parse_biz(input_biz_name)
    # api查询业务
    if real_biz_name is None:
        await session.send(f'未找到您说的业务')
    else:
        await session.send(f'你是否查询以下业务:')
        for biz in data:
            data = await self.search_biz(biz['bk_biz_name'])
            await session.send(json.dumps(data))
```

> CC查询api
```python
# api.py 目录下
from typing import Dict

from component import CC


async def search_biz(bk_username: str, bk_biz_name: str) -> Dict:
    response = await CC().search_business(bk_username=bk_username,
                                          condition={'bk_biz_name': bk_biz_name})
    return response
```

> 利用业务识别算法，识别用户输入业务名称
```python
# stdlib目录下
from typing import List

from component import BizMapper
from .settings import TOP_RANK, PARSE_RATE


async def parse_biz(name: str) -> List:
    bm = BizMapper(top_rank=TOP_RANK)
    await bm.prepare_corpus()
    try:
        result = bm.predict(name)
        if result and result[0]['rate'] > PARSE_RATE:
            return result[:3]
    except (AttributeError, KeyError):
        logger.exception(f'parse_biz_name error {name}')
        return None
```

### 4.测试使用

> 代码检查无误后，重启服务后

```shell
# 创建
cd bk-chatbot/src/backend || exit
sh control stop && sh control start
```

> 对话

```shell
> 业务查询
你想查询哪个业务？
> 业务A
你是否查询以下业务:
{
    "bk_biz_name": 业务A
    "bk_biz_id": 1234
    "oper": "张三"
    ...
}
