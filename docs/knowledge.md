# BK_CHATBOT 知识库使用说明

## 支持QA的存储
* mongo
* 文件存储

## 库目录
```
backend/component/nlp/knowledge/v20220309
```

## 配置文件说明
```
MONGO_DB_HOST              (mongo库域名)
MONGO_DB_PORT              (mongo库端口)
MONGO_DB_NAME              (mongo库名)
MONGO_TABLE_NAME           (mongo库collection名)
MONGO_DB_USERNAME          (mongo库collection名)
MONGO_DB_PASSWORD          (mongo库collection名)
···
# 是否启用从mongo获取语料，默认为False，启用为True
EXAMPLE_CORPUS_PATH = join(CUR_PATH, 'corpus', 'qa.json') (qa json文件配置样例)
EXAMPLE_CORPUS = json.load(open(EXAMPLE_CORPUS_PATH))
# 是否触发训练，默认为False
NEED_TRAIN = False         (是否每次都进行训练)
USE_MONGO = False          (存储引擎选择，是否使用mongo)

SIMILAR_PERCENTAGE = 0.6   (匹配最低概率，可修改)
FILTER_PERCENTAGE = 0.75   (匹配筛选概率，可修改)
```

## 使用
```
from component import fetch_answer

fetch_answer('蓝鲸是什么')
```
