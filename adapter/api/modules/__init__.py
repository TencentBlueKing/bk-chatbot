# -*- coding: utf-8 -*-


class Regex(object):
    NUMBER = r"[0-9]+"
    ROLE_ID = r"[a-z_]+\.[a-z_]+"
    RESULT_TABLE_ID = r"\d+([_a-zA-Z0-9]+)"
    MODEL_ID = r"[_a-zA-Z0-9]+"

    # 没有约束，这里只限定不能为斜杠/
    EXCLUDE_SLASH = r"((?!\/).)*"
