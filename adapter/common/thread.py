# -*- coding: utf-8 -*-

import threading

from adapter.utils.local import get_request, activate_request


class FuncThread(threading.Thread):
    def __init__(self, func, params, result_key, results):
        self.func = func
        self.params = params
        self.result_key = result_key
        self.results = results
        self.requests = get_request()
        super().__init__()

    def run(self):
        activate_request(self.requests)
        if self.params:
            self.results[self.result_key] = self.func(self.params)
        else:
            self.results[self.result_key] = self.func()


class MultiExecuteFunc(object):
    """
    基于多线程的批量并发执行函数
    """

    def __init__(self):
        self.results = {}
        self.task_list = []

    def append(self, result_key, func, params=None):
        if result_key in self.results:
            raise ValueError(f"result_key: {result_key} is duplicate. Please rename it.")
        task = FuncThread(func=func, params=params, result_key=result_key, results=self.results)
        self.task_list.append(task)
        task.start()

    def run(self):
        for task in self.task_list:
            task.join()
        return self.results
