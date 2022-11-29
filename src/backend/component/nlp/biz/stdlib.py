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

import json
from os.path import join
from itertools import chain
from typing import Dict, List, Union, Sequence
from datetime import datetime

import arrow
import jieba
import diskcache as dc

from .config import BIZ_DISK_CACHE_PATH, BIZ_CORPUS_DATA_PATH
from component import BKCloud
from component.config import BK_SUPER_USERNAME


class DiskCache(dc.Cache):
    """
    disk cache.
    """

    def __init__(self, name, cache_dir=None):
        self.name = name
        self.cache_dir = cache_dir or BIZ_DISK_CACHE_PATH
        super(DiskCache, self).__init__(join(self.cache_dir, self.name))


class CorpusConfig:
    """
    corpus config, load cache, set corpus or alias to cache
    and fetch user dictionary
    """
    def __init__(self):
        self.cache = DiskCache("BizMeta")
        self.fields = ["bk_app_abbr", "bk_biz_name", "bk_biz_id"]

    @classmethod
    def _get_timestamp(cls, date, tz="local"):
        return arrow.get(date).replace(tzinfo=tz).timestamp()

    @classmethod
    def _shift_timestamp(cls, date, offset, date_format="YYYY-MM-DD HH:mm:ss"):
        """
        date offset
        """
        assert set(offset.keys()) <= set(["days", "hours", "minutes", "seconds" ]), f"invalid offset({offset})."
        _date_ = arrow.get(date).shift(**offset)
        if isinstance(date, int):
            return _date_.to(tz="Asia/Shanghai").format(date_format)
        elif isinstance(date, (str, datetime)):
            return _date_.format(date_format)
        else:
            raise Exception("invalid datetime(%s)." % date)

    @classmethod
    def _get_now_timestamp(cls, date_format="YYYY-MM-DD HH:mm:ss.SSS") -> str:
        """
        local time
        """
        return arrow.now().replace(tzinfo="Asia/Shanghai").format(date_format)

    def _set_cut_words(self):
        keywords = self.cache.get("bk_biz_name")
        for i in keywords:
            _ws = list(jieba.cut(i))
            self.cache.set(f"KW_{i}", _ws)

    def _do_cache_biz_field(self, field: str, data: List, expire: int):
        self.cache.set(field, [i[field] for i in data if str(i.get(field, '')).strip()], expire=expire)

    async def get_user_dict(self, is_cache=False,
                            keys: Union[str, Sequence[str]] = ["bk_app_abbr", "bk_biz_name"]) -> List:
        """
        fetch user self-define work msg,
        help make work cut more precise
        """
        if is_cache:
            await self.set_corpus_to_cache()

        if isinstance(keys, str):
            return self.cache.get(keys)
        elif isinstance(keys, list):
            result = [self.cache.get(key) for key in keys if self.cache.get(key)]
            return list(chain.from_iterable(result))

        return []

    async def set_corpus_to_cache(self, expire=24 * 60 * 60, with_keywords=False):
        """
        cache biz info, reduce fetch frequency
        """
        cc = BKCloud().bk_service.cc
        data = (await cc.search_business(bk_username=BK_SUPER_USERNAME, fields=self.fields)).get('info', [])
        if not data:
            return

        # precise/fuzzy
        for field in self.fields:
            self._do_cache_biz_field(field, data, expire)

        for i, item in enumerate(data):
            item.pop('default')
            for j in item.values():
                if not str(j).strip():
                    continue

                if str(j).isdigit():
                    j = int(j)
                else:
                    j = j.upper()

                self.cache.set(j, item, expire=expire)

        if with_keywords:
            self._set_cut_words()

    def set_alias_to_cache(self, file) -> List[List]:
        """
        biz alias name
        """
        with open(file=join(BIZ_CORPUS_DATA_PATH, file), mode="r") as f:
            data = json.load(f)
            alias_key_words = []
            for k, v in data.items():
                for i in v:
                    self.cache.set(i, self.cache.get(i, {'bk_biz_name': k}))
                alias_key_words += v

            return alias_key_words

    async def check_corpus(self, keys=["bk_biz_id", "bk_biz_name", "bk_app_abbr"], with_keywords=True):
        for i in keys:
            if i in self.cache:
                continue
            await self.set_corpus_to_cache(with_keywords=with_keywords)
            return
