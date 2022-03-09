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

import os
import io

import jieba
from gensim import corpora, models, similarities
try:
    from pymongo import MongoClient
except ImportError:
    MongoClient = None

from opsbot.log import logger
from .config import (
    USE_MONGO, NEED_TRAIN, EXAMPLE_CORPUS, SIMILAR_WORD, BIZ_MODELS_DIR, STOP_WORDS_PATH,
    MONGO_DB_HOST, MONGO_DB_NAME, MONGO_TABLE_NAME, MONGO_DB_PORT, MONGO_DB_USERNAME, MONGO_DB_PASSWORD,
    FILTER_PERCENTAGE, SIMILAR_PERCENTAGE
)


def get_corpus_wiki(biz_id=None):
    """
    获取语料，
    :param biz_id: 业务id，业务纬度
    :return:
    """
    intent_list = []
    if not USE_MONGO:
        for biz_corpus in EXAMPLE_CORPUS:
            if biz_corpus['data'] and len(biz_corpus['data']) > 0:
                for corpus in biz_corpus['data']:
                    if not biz_id:
                        intent_list.append(
                            {'question': corpus['question'], 'solution': corpus['solution'], 'biz_id': 0})
                    if biz_corpus['biz_id'] == biz_id:
                        intent_list.append(
                            {'question': corpus['question'], 'solution': corpus['solution'], 'biz_id': int(biz_id)})
    else:
        db_name = MONGO_DB_NAME
        collection_name = MONGO_TABLE_NAME
        db_results = []
        client = MongoClient(host=MONGO_DB_HOST, port=MONGO_DB_PORT,
                             username=MONGO_DB_USERNAME, password=MONGO_DB_PASSWORD)
        db = client[db_name]
        collection = db[collection_name]
        cursor = collection.find()
        for i in cursor:
            db_results.append(i)
        client.close()
        if db_results and len(db_results) > 0:
            for intent in db_results:
                if not biz_id:
                    intent_list.append({'question': intent['question'], 'solution': intent['solution'], 'biz_id': 0})
                if 'biz_id' in intent and intent['biz_id'] == biz_id:
                    intent_list.append(
                        {'question': intent['question'], 'solution': intent['solution'], 'biz_id': int(biz_id)})
        else:
            logger.error('执行获取mongo语料数据错误')
    return intent_list


def get_custom_stopwords(stop_words_file):
    """
    创建停用词list，
    :param stop_words_file: 停用词文件
    :return:
    """
    with io.open(stop_words_file, encoding='utf-8')as f:
        stopwords = f.read()
    stopwords_list = stopwords.split('\n')
    custom_stopwords_list = [i for i in stopwords_list]
    return custom_stopwords_list


def filter_stop_word(word_list, stop_word_list):
    """
    过滤停用词
    :param word_list: 需要过滤的词列表
    :param stop_word_list: 停用词列表
    """
    res = list(filter(lambda w: w not in stop_word_list, word_list))
    return res


def similar_questions(doc_test_list):
    question_all_list = []
    list_index = []
    for index, word in enumerate(doc_test_list):
        if SIMILAR_WORD.get(word):
            similar_list = SIMILAR_WORD[word]
            list_index.append((index, similar_list))
    if len(list_index) > 0:
        for i in range(len(list_index)):
            if len(list_index) > 1:
                for j in range(i + 1, len(list_index)):
                    for similar_word_i in list_index[i][1]:
                        doc_test_list[list_index[i][0]] = similar_word_i
                        for similar_word_j in list_index[j][1]:
                            doc_test_list[list_index[j][0]] = similar_word_j
                            question_all_list.append(list(doc_test_list))
            else:
                for similar_word_i in list_index[i][1]:
                    doc_test_list[list_index[i][0]] = similar_word_i
                    question_all_list.append(list(doc_test_list))

    else:
        question_all_list.append(list(doc_test_list))
    return question_all_list


def match_model(question_word, model_tfidf, model_ind, model_dictionary):
    """
    使用模型匹配问题
    :param model_dictionary: 词袋
    :param model_tfidf: 语料库模型
    :param model_ind: 语料转换为LSI,并已经索引
    :param question_word:  所有待查询的词，已经获取了同义词
    """
    result = []
    for question_test_list in question_word:
        # 转换为向量
        doc_test_vec = model_dictionary.doc2bow(question_test_list)
        # 分析相似性
        sim = model_ind[model_tfidf[doc_test_vec]]
        match_result = sorted(enumerate(sim), key=lambda item: -item[1])
        if len(result) == 0:
            result = match_result
        else:
            if match_result[0][1] > result[0][1]:
                result = match_result
    return result


def filter_by_similar(sorted_list):
    """
    若多于SIMILAR_PERCENTAGE的有超过5个，则再次过滤
    :param sorted_list: 正排序的结果
    """
    sorted_list.sort(key=lambda k: k['similar'], reverse=True)
    filter_list = list(filter(lambda x: x['similar'] > FILTER_PERCENTAGE, sorted_list))
    if len(filter_list) == 0:
        ret = sorted_list[0:5]
    else:
        ret = filter_list[0:5]
    return ret


def sort_by_similar(sort, biz_data_list):
    sort_res = []
    for i in sort:
        if i[1] >= SIMILAR_PERCENTAGE:
            temp = {'question': biz_data_list[i[0]]['question'],
                    'solution': biz_data_list[i[0]]['solution'],
                    'biz_id': biz_data_list[i[0]]['biz_id'],
                    'similar': float(round(i[1], 2))}
            if len(sort_res) == 0:
                sort_res.append(temp)
            else:
                flag = False
                for tmp in sort_res:
                    if tmp['question'] == temp['question']:
                        flag = True
                        break
                if not flag:
                    sort_res.append(temp)
    return sort_res


def get_models_path(biz_id):
    dir_type = 'mongo' if USE_MONGO else 'text'
    dictionary_path = os.path.join(BIZ_MODELS_DIR, dir_type, str(biz_id), '{}.dict'.format(biz_id))
    index_path = os.path.join(BIZ_MODELS_DIR, dir_type, str(biz_id), '{}.index'.format(biz_id))
    tfidf_path = os.path.join(BIZ_MODELS_DIR, dir_type, str(biz_id), '{}.tfidf'.format(biz_id))
    return dictionary_path, index_path, tfidf_path


def get_model(biz_id):
    """
    从本地文件加载模型
    :param biz_id: 业务ID
    """
    dictionary_path, index_path, tfidf_path = get_models_path(biz_id)
    dictionary = ""
    index = ""
    tfidf = ""
    if (os.path.isfile(dictionary_path)) and (os.path.isfile(index_path)) and (os.path.isfile(tfidf_path)):
        dictionary = corpora.Dictionary.load(dictionary_path)
        index = similarities.SparseMatrixSimilarity.load(index_path)
        tfidf = models.TfidfModel.load(tfidf_path)

    return tfidf, index, dictionary


def train_model(biz_data_list, stop_word_list, biz_id=None):
    """
    根据业务语料来训练模型
    :param biz_data_list: 某个业务的语料
    """
    text_list = []
    if len(biz_data_list) == 1:
        tmp_data = {'utterance': '你好', 'intent_name': '你好', 'biz_id': 0}
        biz_data_list.append(tmp_data)
    for w in biz_data_list:
        utterance = w['question']
        cut_res = jieba.lcut(utterance.lower())
        each_text_list = [w for w in cut_res if w not in stop_word_list]
        # 分词和去掉停用词之后的语料
        text_list.append(each_text_list)
    # 模型文件存储路径
    if not biz_id:
        biz_id = 0
    dir_type = 'mongo' if USE_MONGO else 'text'
    dir_path = os.path.join(BIZ_MODELS_DIR, dir_type, str(biz_id))
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    dictionary_path, index_path, tfidf_path = get_models_path(biz_id)
    # 获取词袋(字典)
    dictionary = corpora.Dictionary(text_list)
    dictionary.save(dictionary_path)
    # 制作语料库，产生稀疏文档向量
    corpus = [dictionary.doc2bow(text) for text in text_list]
    # 对语料库建模,即训练转换模型
    tfidf = models.TfidfModel(corpus)
    tfidf.save(tfidf_path)
    # 将语料转换为LSI,并索引
    index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=len(dictionary.keys()))
    index.save(index_path)
    return tfidf, index, dictionary


def fetch_answer(msg_content, biz_id=None):
    # 获取语料
    biz_data_list = get_corpus_wiki(biz_id)
    # 对输入内容进行分词
    cut_word_res = jieba.lcut(msg_content.lower())
    # 停用词列表
    stop_word_list = get_custom_stopwords(STOP_WORDS_PATH)
    # 去除停用词
    question_word = filter_stop_word(cut_word_res, stop_word_list)
    question_all_list = similar_questions(question_word)
    # 获取业务模型
    if not biz_id:
        biz_id = 0
    tfidf, ind, dictionary = get_model(biz_id)
    # 获取存储的模型失败，重新训练
    if NEED_TRAIN or not tfidf:
        # 模型训练
        tfidf, ind, dictionary = train_model(biz_data_list, stop_word_list, biz_id)
    # 根据模型获取结果
    similar_result = match_model(question_all_list, tfidf, ind, dictionary)
    # 结果排序
    sorted_result = sort_by_similar(similar_result, biz_data_list)
    intent_list = filter_by_similar(sorted_result)
    return intent_list
