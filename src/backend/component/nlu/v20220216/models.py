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

import re
import time
import itertools
from typing import List, Tuple, Dict, Iterable
from collections import deque

import aiofiles
import jieba
from gensim import corpora, models, similarities

from component import BKCloud
from component.exceptions import SlotLocMatchError
from .config import (
    BASE_DICT_PATH, STOP_WORDS_PATH,
    SIMILAR_WORD_LIB, BASE_CONFIDENCE
)


class IntentRecognition:
    def __init__(self, bk_env: str = 'v7'):
        self.bk_env = bk_env
        self._bk_cloud = BKCloud(bk_env)
        self._backend = self._bk_cloud.bk_service.backend
        jieba.load_userdict(BASE_DICT_PATH)

    async def _load_corpus_text(self, **kwargs) -> List:
        db_intents = await self._backend.describe('intents', **kwargs)
        if not db_intents:
            return None

        intent_map = {intent['id']: intent for intent in db_intents}
        db_utterances = await self._backend.describe('utterances', index_id__in=list(intent_map.keys()))
        return list(itertools.chain(*[
            [
                {
                    'utterance': sentence,
                    'intent_id': intent_map[utterance['index_id']]['id'],
                    'intent_name': intent_map[utterance['index_id']]['intent_name'],
                    'is_commit': intent_map[utterance['index_id']]['is_commit'],
                    'status': intent_map[utterance['index_id']]['status'],
                    'available_user': intent_map[utterance['index_id']]['available_user'],
                    'available_group': intent_map[utterance['index_id']]['available_group'],
                    'biz_id': intent_map[utterance['index_id']]['biz_id'],
                    'updated_by': intent_map[utterance['index_id']]['updated_by'],
                    'approver': intent_map[utterance['index_id']]['approver'],
                    'notice_discern_success': intent_map[utterance['index_id']].get('notice_discern_success', True),
                    'notice_start_success': intent_map[utterance['index_id']].get('notice_start_success', True),
                    'notice_exec_success': intent_map[utterance['index_id']].get('notice_exec_success', True),
                    'bk_env': self.bk_env
                } for sentence in utterance['content']
            ] for utterance in db_utterances
        ]))

    @classmethod
    async def _get_custom_stopwords(cls) -> List:
        async with aiofiles.open(STOP_WORDS_PATH, mode='r', encoding='utf-8') as f:
            stopwords = await f.read()
        return stopwords.split('\n')

    @classmethod
    def _filter_stop_word(cls, src_word_list: List, stop_word_list: List) -> List:
        return [word for word in src_word_list if word not in stop_word_list]

    @classmethod
    def _similar_questions(cls, question_word: List) -> List:
        """
        replace similar word,
        generate more text
        """
        word_matrix = []
        for word in question_word:
            if word in SIMILAR_WORD_LIB:
                word_matrix.append(SIMILAR_WORD_LIB[word])
            else:
                word_matrix.append([word])

        similar_question_word = []
        for item in itertools.product(*word_matrix):
            similar_question_word.append(list(item))

        return similar_question_word

    @classmethod
    def _train_model(cls, utterances: List, stop_words: List) -> Tuple:
        """
        获取词袋(字典)
        制作语料库，产生稀疏文档向量
        对语料库建模,即训练转换模型
        将语料转换为LSI,并索引
        """
        if not utterances[1:]:
            utterances.append({'intent_id': 0, 'is_commit': False, 'status': False, 'utterance': '你好',
                               'available_group': [], 'intent_name': '你好', 'available_user': []})
        cur_word_group = [
            [
                word for word in jieba.lcut(utterance['utterance'].lower()) if word not in stop_words
            ] for utterance in utterances
        ]
        dictionary = corpora.Dictionary(cur_word_group)
        corpus = [dictionary.doc2bow(text) for text in cur_word_group]
        tf_idf = models.TfidfModel(corpus)
        index = similarities.SparseMatrixSimilarity(tf_idf[corpus], num_features=len(dictionary.keys()))
        return tf_idf, index, dictionary

    @classmethod
    def _match_model(cls, question_words: List, model_tf_idf, model_index, model_dictionary) -> List:
        """
        转换为向量
        分析相似性
        """
        result = []
        for question_word in question_words:
            doc_vec = model_dictionary.doc2bow(question_word)
            sim = model_index[model_tf_idf[doc_vec]]
            match_result = sorted(enumerate(sim), key=lambda item: -item[1])
            try:
                if match_result[0][1] > result[0][1]:
                    result = match_result
            except IndexError:
                result = match_result
        return result

    @classmethod
    def _sort_by_similar(cls, related_question_word: List, utterances: List) -> List:
        filtered_utterances = [
            {
                'utterance': utterances[word[0]]['utterance'], 'id': utterances[word[0]]['intent_id'],
                'intent_name': utterances[word[0]]['intent_name'], 'intent_id': utterances[word[0]]['intent_id'],
                'is_commit': utterances[word[0]]['is_commit'], 'status': utterances[word[0]]['status'],
                'updated_by': utterances[word[0]]['updated_by'], 'approver': utterances[word[0]]['approver'],
                'available_user': utterances[word[0]]['available_user'],
                'available_group': utterances[word[0]]['available_group'],
                'biz_id': utterances[word[0]]['biz_id'], 'similar': float(round(word[1], 2)),
                'notice_discern_success': utterances[word[0]].get('notice_discern_success', True),
                'notice_start_success': utterances[word[0]].get('notice_start_success', True),
                'notice_exec_success': utterances[word[0]].get('notice_exec_success', True),
                'bk_env': utterances[word[0]]['bk_env']
            } for word in related_question_word if word[1] >= BASE_CONFIDENCE
        ]

        unique_utterances = []
        for utterance in filtered_utterances:
            if not any(utterance['intent_name'] == item['intent_name'] for item in unique_utterances):
                unique_utterances.append(utterance)
        unique_utterances.sort(key=lambda k: k['similar'], reverse=True)
        return unique_utterances[:5]

    async def preprocess_text(self, text: str) -> List:
        cmd = re.split(r"\?+|\s+", text)[0]
        cut_words = jieba.lcut(cmd.lower())
        stop_words = await self._get_custom_stopwords()
        question_words = self._filter_stop_word(cut_words, stop_words)
        return question_words, stop_words

    async def fetch_intent(self, text: str, **kwargs) -> List:
        utterances = await self._load_corpus_text(**kwargs)
        if not utterances:
            return None
        question_words, stop_words = await self.preprocess_text(text)
        similar_question_words = self._similar_questions(question_words)
        tf_idf, index, dictionary = self._train_model(utterances, stop_words)

        related_question_word = self._match_model(similar_question_words, tf_idf, index, dictionary)
        related_question_word = self._sort_by_similar(related_question_word, utterances)
        return related_question_word


class SlotRecognition:
    DEFAULT_SLOTS = ['${USER_ID}', '${GROUP_ID}']
    STUPID_PATTERNS = ['.*', '^.+$']

    def __init__(self, intent: Dict, bk_env: str = 'v7'):
        self._bk_cloud = BKCloud(bk_env)
        self._backend = self._bk_cloud.bk_service.backend
        self.intent = intent

    async def load_slots(self) -> List:
        tasks = await self._backend.describe('tasks', index_id=int(self.intent.get('id')))
        if tasks:
            slots = tasks[0]['slots']
            slots.reverse()
            for slot in slots:
                slot.setdefault('value', '')
            return slots
        return None

    def _preprocess_text(self, text: str, slots: List) -> Iterable:
        if all([slot['pattern'] in self.STUPID_PATTERNS for slot in slots]):
            clean_params = re.split(r"\?+|\s+", text)[1:]
        else:
            params = re.split(r"\?+|\s+", str(''.join([letter if ord(letter) < 128 else '?' for letter in text])))
            clean_params = [
                letter.strip() for letter in params if letter and letter not in self.intent.get('utterance', '')
            ]
        return deque(clean_params)

    def match_time(self, slots: List) -> bool:
        if 'timer' in self.intent:
            if 'timestamp' not in self.intent['timer'] or \
                    self.intent['timer']['timestamp'] < time.strftime('%Y-%m-%d %H:%M:%S'):
                return False

            time_str = self.intent['timer']['time_str']
            for slot in slots:
                if slot['value'] in self.DEFAULT_SLOTS or slot['pattern'] in self.STUPID_PATTERNS:
                    continue
                result = re.compile(slot['pattern']).search(time_str)
                if result:
                    return False
            return True
        return False

    def match_slot(self, text: str, slots: List) -> List:
        """
        1, default value can not be used
        2, max len match method
        3, if contain special ${}, catch it by order
        4, add biz special function
        """
        clean_params = self._preprocess_text(text, slots)
        for slot in slots:
            if slot['value'] in self.DEFAULT_SLOTS:
                continue

            if slot['pattern'] in self.STUPID_PATTERNS:
                try:
                    slot['value'] = clean_params.popleft()
                except IndexError:
                    pass
                continue

            max_len = 0
            pattern = re.compile(slot['pattern'])
            for segment in clean_params:
                result = pattern.search(segment)
                seg_len = len(result.group()) if result else 0
                if seg_len > max_len:
                    slot['value'] = result.group()
                    max_len = seg_len
            if slot['value']:
                try:
                    clean_params.remove(slot['value'])
                except ValueError:
                    pass
        return slots

    async def fetch_slot(self, text: str = '') -> List:
        slots = await self.load_slots()
        if slots:
            try:
                slots = getattr(self.BizFilter(text), f'filter_{self.intent["biz_id"]}')(slots)
            except (AttributeError, SlotLocMatchError):
                slots = self.match_slot(text, slots)
        return slots

    class BizFilter:
        """
        eg: you can define function like this
        def filter_xxx(self, slots: List) -> List:
            return self.loc_match(slots)
        """

        def __init__(self, text: str):
            self.text = text

        def loc_match(self, slots: List) -> List:
            result = re.findall(r'\$\{.*?\=.*?\}', self.text)
            if len(result) != len(slots):
                raise SlotLocMatchError

            for segment in result:
                name, value = segment[2: -1].split('=')
                for slot in slots:
                    if slot['name'] == name:
                        slot['value'] = value
            return slots
