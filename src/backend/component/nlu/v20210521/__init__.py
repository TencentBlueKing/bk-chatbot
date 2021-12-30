
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
import json
import io
import re
import jieba
from gensim import corpora, models, similarities

from component import Backend

CUR_PATH = os.path.dirname(os.path.abspath(__file__))
BASE_DICT_PATH = os.path.join(CUR_PATH, 'corpus', 'base_dict.txt')
STOP_WORDS_PATH = os.path.join(CUR_PATH, 'corpus', 'stopwords.txt')
SIMILAR_WORD_PATH = os.path.join(CUR_PATH, 'corpus', 'similar_word.json')
similar_word = json.load(open(SIMILAR_WORD_PATH, encoding='utf-8'))
jieba.load_userdict(BASE_DICT_PATH)


async def get_slots(intent_id):
    slot_list = []
    try:
        task_list = await Backend().describe('tasks', index_id=intent_id)
        slots = task_list[0]['slots']
        for slot in slots:
            slot.setdefault('value', '')
            slot_list.append(slot)
    except IndexError:
        return slot_list
    else:
        return slot_list


def get_slot_data(msg, reglist):
    reg_msg_tmp = re.split(r"\?+|\s+", str(''.join([i if ord(i) < 128 else '?' for i in msg])))
    reg_msg = list(filter(None, [x.strip() for x in reg_msg_tmp]))
    reg_msg_list_tmp = []
    for m in range(0, len(reg_msg)):
        reg_msg_dir = {}
        str_num = 0
        for n in range(0, len(reglist)):
            pat = re.compile(reglist[n]['pattern'])
            regstr_obj = pat.search(reg_msg[m])
            if regstr_obj and len(regstr_obj.group()) > str_num:
                reg_msg_dir['value'] = regstr_obj.group()
                reg_msg_dir['value'] = regstr_obj.group()
                reg_msg_dir['id'] = reglist[n]['id']
                reg_msg_dir['pattern'] = reglist[n]['pattern']
                reg_msg_dir['name'] = reglist[n]['name']
                str_num = len(regstr_obj.group())
        if reg_msg_dir:
            reg_msg_list_tmp.append(reg_msg_dir)
        for a in reg_msg_list_tmp:
            for b in reglist:
                if str(a['id']) == str(b['id']):
                    b['value'] = a['value']
    return reglist


async def fetch_slot(msg_content, intent_id):
    """
    获取slot值，
    :param msg_content: 用户语句
    :param intent_id: 意图id
    :return:
    """
    slot_list = await get_slots(intent_id)
    reg_list = get_slot_data(msg_content, slot_list)
    return reg_list


async def get_corpus_text(**kwargs):
    """
    获取语料，
    :param biz_id: 业务id，业务纬度，内部群聊场景
    :param user_id: 用户id，单聊的场景
    :return:
    """
    backend = Backend()
    intent_list = []
    db_intents = await backend.describe('intents', **kwargs)
    if len(db_intents) > 0:
        for intent in db_intents:
            intent_id = intent['id']
            intent_name = intent['intent_name']
            is_commit = intent['is_commit']
            status = intent['status']
            available_user = intent['available_user']
            available_group = intent['available_group']
            approver = intent['approver']
            biz_id = intent['biz_id']
            updated_by = intent['updated_by']
            # todo decrease check db frequently
            db_utterances = await backend.describe('utterances', index_id=intent_id)
            if len(db_utterances) > 0:
                utterance_list = db_utterances[0]['content']
                for utterance in utterance_list:
                    intent_list.append(
                        {'intent_id': intent_id, 'intent_name': intent_name, 'is_commit': is_commit, 'status': status,
                         'available_user': available_user, 'available_group': available_group, 'biz_id': biz_id,
                         'utterance': utterance, 'updated_by': updated_by, 'approver': approver})
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
        if similar_word.get(word):
            similar_list = similar_word[word]
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
    若多于similar_percentage=0.6的有超过5个，则再次过滤
    :param sorted_list: 正排序的结果
    """
    filter_percentage = 0.75
    sorted_list.sort(key=lambda k: k['similar'], reverse=True)
    filter_list = list(filter(lambda x: x['similar'] > filter_percentage, sorted_list))
    if len(filter_list) == 0:
        ret = sorted_list[0:5]
    else:
        ret = filter_list[0:5]
    return ret


def sort_by_similar(sort, biz_data_list):
    similar_percentage = 0.6
    sort_res = []
    for i in sort:
        if i[1] >= similar_percentage:
            temp = {'utterance': biz_data_list[i[0]]['utterance'], 'id': biz_data_list[i[0]]['intent_id'],
                    'intent_name': biz_data_list[i[0]]['intent_name'], 'intent_id': biz_data_list[i[0]]['intent_id'],
                    'is_commit': biz_data_list[i[0]]['is_commit'], 'status': biz_data_list[i[0]]['status'],
                    'updated_by': biz_data_list[i[0]]['updated_by'], 'approver': biz_data_list[i[0]]['approver'],
                    'available_user': biz_data_list[i[0]]['available_user'],
                    'available_group': biz_data_list[i[0]]['available_group'], 'biz_id': biz_data_list[i[0]]['biz_id'],
                    'similar': float(round(i[1], 2))}
            if len(sort_res) == 0:
                sort_res.append(temp)
            else:
                flag = False
                for tmp in sort_res:
                    if tmp['intent_name'] == temp['intent_name']:
                        flag = True
                        break
                if not flag:
                    sort_res.append(temp)
    return sort_res


def train_model(biz_data_list, stop_word_list):
    """
    根据业务语料来训练模型
    :param biz_data_list: 某个业务的语料
    """
    text_list = []
    if len(biz_data_list) == 1:
        tmp_data = {'intent_id': 0, 'is_commit': False, 'status': False, 'utterance': '你好',
                    'available_group': [], 'intent_name': '你好', 'available_user': []}
        biz_data_list.append(tmp_data)
    for w in biz_data_list:
        utterance = w['utterance']
        cut_res = jieba.lcut(utterance.lower())
        each_text_list = [w for w in cut_res if w not in stop_word_list]
        # 分词和去掉停用词之后的语料
        text_list.append(each_text_list)
    # 获取词袋(字典)
    dictionary = corpora.Dictionary(text_list)
    # 制作语料库，产生稀疏文档向量
    corpus = [dictionary.doc2bow(text) for text in text_list]
    # 对语料库建模,即训练转换模型
    tfidf = models.TfidfModel(corpus)
    # 将语料转换为LSI,并索引
    index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=len(dictionary.keys()))
    return tfidf, index, dictionary


async def fetch_intent(msg_content, **kwargs):
    # 获取语料
    biz_data_list = await get_corpus_text(**kwargs)
    # 对输入内容进行分词
    cut_word_res = jieba.lcut(msg_content.lower())
    # 停用词列表
    stop_word_list = get_custom_stopwords(STOP_WORDS_PATH)
    # 去除停用词
    question_word = filter_stop_word(cut_word_res, stop_word_list)
    question_all_list = similar_questions(question_word)
    # 模型训练
    tfidf, ind, dictionary = train_model(biz_data_list, stop_word_list)
    # 根据模型获取结果
    similar_result = match_model(question_all_list, tfidf, ind, dictionary)
    # 结果排序
    sorted_result = sort_by_similar(similar_result, biz_data_list)
    intent_list = filter_by_similar(sorted_result)
    return intent_list
