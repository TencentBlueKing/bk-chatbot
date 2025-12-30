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

import pickle
import regex as re
import arrow
import json
import os

from .StringPreHandler import StringPreHandler
from .TimePoint import TimePoint
from .TimeUnit import TimeUnit


# 时间表达式识别的主要工作类
class TimeNormalizer:
    def __init__(self, isPreferFuture=True):
        self.isPreferFuture = isPreferFuture
        self.pattern, self.holi_solar, self.holi_lunar = self.init()

    # 这里对一些不规范的表达做转换
    def _filter(self, input_query):
        # 这里对于下个周末这种做转化 把个给移除掉
        input_query = StringPreHandler.number_translator(input_query)

        rule = u"[0-9]月[0-9]"
        pattern = re.compile(rule)
        match = pattern.search(input_query)
        if match:
            index = input_query.find('月')
            rule = u"日|号"
            pattern = re.compile(rule)
            match = pattern.search(input_query[index:])
            if not match:
                rule = u"[0-9]月[0-9]+"
                pattern = re.compile(rule)
                match = pattern.search(input_query)
                if match:
                    end = match.span()[1]
                    input_query = input_query[:end] + '号' + input_query[end:]

        rule = u"月"
        pattern = re.compile(rule)
        match = pattern.search(input_query)
        if not match:
            input_query = input_query.replace('个', '')

        input_query = input_query.replace('中旬', '15号')
        input_query = input_query.replace('傍晚', '午后')
        input_query = input_query.replace('大年', '')
        input_query = input_query.replace('五一', '劳动节')
        input_query = input_query.replace('白天', '早上')
        input_query = input_query.replace('：', ':')
        return input_query

    def init(self):
        fpath = os.path.dirname(__file__) + '/resource/reg.pkl'
        try:
            with open(fpath, 'rb') as f:
                pattern = pickle.load(f)
        except Exception:
            with open(os.path.dirname(__file__) + '/resource/regex.txt', 'r', encoding="utf-8") as f:
                content = f.read()
            p = re.compile(content)
            with open(fpath, 'wb') as f:
                pickle.dump(p, f)
            with open(fpath, 'rb') as f:
                pattern = pickle.load(f)
        with open(os.path.dirname(__file__) + '/resource/holi_solar.json', 'r', encoding='utf-8') as f:
            holi_solar = json.load(f)
        with open(os.path.dirname(__file__) + '/resource/holi_lunar.json', 'r', encoding='utf-8') as f:
            holi_lunar = json.load(f)
        return pattern, holi_solar, holi_lunar

    def parse(self, target, timeBase=arrow.now()):
        """
        TimeNormalizer的构造方法，timeBase取默认的系统当前时间
        :param timeBase: 基准时间点
        :param target: 待分析字符串
        :return: 时间单元数组
        """
        self.isTimeSpan = False
        self.invalidSpan = False
        self.timeSpan = ''
        self.target = self._filter(target)
        self.timeBase = arrow.get(timeBase).format('YYYY-M-D-H-m-s')
        self.nowTime = timeBase
        self.oldTimeBase = self.timeBase
        self._pre_handling()
        self.timeToken = self._time_ex()
        dic = {}
        res = self.timeToken

        if self.isTimeSpan:
            if self.invalidSpan:
                dic['error'] = 'no time pattern could be extracted.'
            else:
                # result = {}
                # dic['type'] = 'timedelta'
                # dic['timedelta'] = self.timeSpan
                # index = dic['timedelta'].find('days')
                # days = int(dic['timedelta'][:index - 1])
                # result['year'] = int(days / 365)
                # result['month'] = int(days / 30 - result['year'] * 12)
                # result['day'] = int(days - result['year'] * 365 - result['month'] * 30)
                # index = dic['timedelta'].find(',')
                # time = dic['timedelta'][index + 1:]
                # time = time.split(':')
                # result['hour'] = int(time[0])
                # result['minute'] = int(time[1])
                # result['second'] = int(time[2])
                # dic['timedelta'] = result
                dic = {'timestamp': self.timeSpan, 'type': 'timestamp'}
        else:
            if len(res) == 0:
                dic['error'] = 'no time pattern could be extracted.'
            elif len(res) == 1:
                dic['type'] = 'timestamp'
                dic['timestamp'] = res[0].time.format("YYYY-MM-DD HH:mm:ss")
            else:
                dic['type'] = 'timespan'
                dic['timespan'] = [res[0].time.format("YYYY-MM-DD HH:mm:ss"), res[1].time.format("YYYY-MM-DD HH:mm:ss")]
        return dic

    def _pre_handling(self):
        """
        待匹配字符串的清理空白符和语气助词以及大写数字转化的预处理
        :return:
        """
        self.target = StringPreHandler.del_keyword(self.target, u"\\s+")  # 清理空白符
        self.target = StringPreHandler.del_keyword(self.target, u"[的]+")  # 清理语气助词
        self.target = StringPreHandler.number_translator(self.target)  # 大写数字转化

    def _time_ex(self):
        """

        :param target: 输入文本字符串
        :param timeBase: 输入基准时间
        :return: TimeUnit[]时间表达式类型数组
        """
        endline = -1
        rpointer = 0
        temp = []

        match = self.pattern.finditer(self.target)
        for m in match:
            startline = m.start()
            if startline == endline:
                rpointer -= 1
                temp[rpointer] = temp[rpointer] + m.group()
            else:
                temp.append(m.group())
            endline = m.end()
            rpointer += 1
        res = []
        contextTp = TimePoint()
        for i in range(0, rpointer):
            # 这里是一个类嵌套了一个类
            res.append(TimeUnit(temp[i], self, contextTp))
            contextTp = res[i].tp

        res = self._filter_time_unit(res)
        return res

    def _filter_time_unit(self, tu_arr):
        """
        过滤timeUnit中无用的识别词。无用识别词识别出的时间是1970.01.01 00:00:00(fastTime=0)
        :param tu_arr:
        :return:
        """
        if (tu_arr is None) or (len(tu_arr) < 1):
            return tu_arr
        res = []
        for tu in tu_arr:
            if tu.time.timestamp != 0:
                res.append(tu)
        return res
