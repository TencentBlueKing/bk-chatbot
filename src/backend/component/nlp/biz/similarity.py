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

import math
from collections import Counter
from typing import SupportsFloat, Dict

import jieba
import jieba.analyse
import Levenshtein
from xpinyin import Pinyin

from .stdlib import DiskCache


class StringSimilarity:
    def __init__(self):
        self.cache = DiskCache("BizMeta")
        self.pin_yin = Pinyin()

    @classmethod
    def _get_cosine(cls, vector_a: Dict, vector_b: Dict) -> SupportsFloat:
        intersection = set(vector_a.keys()) & set(vector_b.keys())
        numerator = sum([vector_a[x] * vector_b[x] for x in intersection])
        sum1 = sum([vector_a[x] ** 2 for x in vector_a.keys()])
        sum2 = sum([vector_b[x] ** 2 for x in vector_b.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    def _text_to_vector(self, text):
        kws = self.cache.get(f"KW_{text}")
        if kws:
            return Counter(kws)

        return Counter(list(jieba.cut(text, use_paddle=True)))

    @classmethod
    def _is_contain_chinese(cls, check_str):
        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

    def text_similarity(self, param_a: str, param_b: str, method='cosine') -> SupportsFloat:
        param_a = param_a.strip()
        param_b = param_b.strip()
        if len(set(param_a) & set(param_b)) == 0:
            return 0.0

        if method == "Levenshtein":
            return Levenshtein.ratio(param_a, param_b)
        elif method == "cosine":
            return self._get_cosine(self._text_to_vector(param_a), self._text_to_vector(param_b))

        raise Exception("error method not supported!")

    def fit_similarity(self, param_a: str, param_b: str) -> int:
        """
        fit business knowledge for similarity
        """
        if self._is_contain_chinese(param_a) == self._is_contain_chinese(param_b) and \
                Levenshtein.ratio(param_a, param_b) == 0:
            return 0

        s1 = Levenshtein.ratio(self.pin_yin.get_initials(param_a, ''), self.pin_yin.get_initials(param_b, ''))
        s2 = Levenshtein.ratio(param_a, param_b)

        t1 = self.pin_yin.get_pinyin(param_a, '-').split('-')
        t2 = self.pin_yin.get_pinyin(param_b, '-').split('-')
        s3 = 0.2 * self._get_cosine(Counter([t1[0], t1[-1]]), Counter([t2[0], t2[-1]])) + 0.8 * self._get_cosine(
            Counter([param_a[0], param_a[-1]]), Counter([param_b[0], param_b[-1]]))

        return round(0.6 * (s1 + s2) / 2 + 0.4 * s3, 4)
