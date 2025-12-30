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

import functools
from os.path import join
from typing import Dict, List, Callable

import jieba.analyse
from pycorrector import set_custom_confusion_dict
from pycorrector.bert import bert_corrector
from pycorrector.corrector import Corrector

from .stdlib import CorpusConfig, DiskCache
from .config import BIZ_CORPUS_DATA_PATH, BIZ_JIEBA_POS
from .similarity import StringSimilarity


class BizMapper:
    def __init__(self, with_ec=False, top_rank=5, threshold=0.5,
                 stop_dict="stopwords.txt", user_dict="userdict.txt", alias_dict="alias.json"):
        """
        corrector ---> cut ---> concise keyword ---> match biz
        """
        self.ec = None
        self.top_rank = top_rank
        self.with_ec = with_ec
        if self.with_ec:
            self.ec = ErrorCorrect()
        self.cc = CorpusConfig()
        self.ss = StringSimilarity()
        self.threshold = threshold
        self.key_words = []
        self.cache = DiskCache("BizMeta")

        if stop_dict:
            jieba.analyse.set_stop_words(join(BIZ_CORPUS_DATA_PATH, stop_dict))
        if user_dict:
            jieba.load_userdict(join(BIZ_CORPUS_DATA_PATH, user_dict))
        self.alias_key_words = []
        if alias_dict:
            self.alias_key_words = self.cc.set_alias_to_cache(alias_dict)

    async def prepare_corpus(self, is_cache=False, keys=["bk_biz_id", "bk_biz_name", "bk_app_abbr"]):
        await self.cc.check_corpus(keys=keys)
        self.key_words = await self.cc.get_user_dict(is_cache=is_cache)
        for i in self.key_words:
            jieba.add_word(i)
        self.key_words += self.alias_key_words
        self.key_words = list(set(self.key_words))

    def explore_similarity_keywords(self, word, func: Callable, **kwargs) -> Dict:
        """
        fetch word related keyword top_rank
        """
        sims = list(map(functools.partial(func, param_b=word, **kwargs), self.key_words))
        sims_top_rank = sorted(sims, reverse=True)[:self.top_rank]
        result = {k: round(v, 4) for k, v in dict(zip(self.key_words, sims)).items() if
                  v and v in sims_top_rank and v > self.threshold}
        return result

    def _is_ABBR(self, words) -> bool:
        return len(words) == 1 and words[0] in self.cache

    def predict(self, text, with_weight=False) -> List:
        """
        fetch top_rank biz list
        """
        if self.with_ec:
            text = self.ec.correct(text)[0]  # 会话文本，一般情况下皆属于MicroText

        # doc
        if (text in self.cache) or (text.upper() in self.cache):
            target = self.cache.get(text) or self.cache.get(text.upper())
            return [{'bk_biz_id': text, 'bk_biz_name': target.get("bk_biz_name"), 'rate': 1.0}]

        # tokenizer nlu
        words = jieba.analyse.extract_tags(text, topK=self.top_rank,
                                           withWeight=with_weight, allowPOS=BIZ_JIEBA_POS)
        base_map = {}
        base_sim = {}

        for i in words:
            _w = i[0] if with_weight else i
            if str(_w).isdigit():
                tmp = self.cache.get(int(_w))
                if tmp:
                    base_map[tmp.get("bk_biz_name")] = 0.9
            elif _w in self.cache or _w.upper() in self.cache:
                tmp = self.cache.get(_w) or self.cache.get(_w.upper())
                if tmp:
                    base_map[tmp.get("bk_biz_name")] = 1 if len(words) == 1 and words[0] == text else 0.9  # 无损
            else:
                ret = self.explore_similarity_keywords(_w, func=self.ss.fit_similarity)
                for k, v in ret.items():
                    if k in base_sim:
                        base_sim[k] += ret[k] * 0.2
                        base_sim[k] = min(base_sim[k], 1.0)
                    else:
                        base_sim[k] = v / (len(words) + 0.1)

        if self._is_ABBR(words):
            text = text.replace(words[0], self.cache.get(words[0], {}).get("bk_biz_name"))
        full_text_mapped = self.explore_similarity_keywords(text, func=self.ss.text_similarity, method="Levenshtein")
        # summary
        for k, v in full_text_mapped.items():
            if k in base_sim:
                base_sim[k] = max(base_sim[k], v)
            else:
                base_sim[k] = v

        if not base_sim:
            return []

        return [{'bk_biz_id': self.cache.get(item[0]).get('bk_biz_id'),
                 'bk_biz_name': self.cache.get(item[0]).get('bk_biz_name'), 'rate': item[1]} for item in
                sorted(base_sim.items(), key=lambda x: x[1], reverse=True)]


class ErrorCorrect:
    def __init__(self, mode="bert", custom_confusion_white="custom_confusion_white.txt"):
        """
        基于拼单、DL学习框架下的纠错功能: 音似、形似错字（或变体字）纠正，可用于中文拼音、笔画输入法的错误纠正
        :param mode: 支持BERT（基于深度学习）以及rULE方式（基于统计方式）
        :param custom_confusion_white: 误杀加白；
        """
        if mode not in ("bert", "rule"):
            raise ("error method({}), and the system supports bert or rule!".format(mode))
        self.mode = mode
        # 初始化纠错环境，加载纠错模型
        if mode == "rule":  # 字典方式预测
            self.md = Corrector()
            self._correct = self.md.correct
        else:  # 使用深度学习纠错
            self.md = bert_corrector.BertCorrector()
            self._correct = self.md.bert_correct
        self.md.check_detector_initialized()  # 一定要加否则纠错时会刷空用户自定义词典；
        # 纠错误杀加白；
        self.custom_confusion_white = custom_confusion_white
        set_custom_confusion_dict(path=join(BIZ_CORPUS_DATA_PATH, custom_confusion_white))

    def correct(self, text):
        return self._correct(text)

