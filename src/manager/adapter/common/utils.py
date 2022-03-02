# -*- coding: utf-8 -*-
"""
开发框架公用方法
1. 页面输入内容转义（防止xss攻击）
from common.utils import html_escape, url_escape, texteditor_escape
2. 转义html内容
html_content = html_escape(input_content)
3. 转义url内容
url_content = url_escape(input_content)
4. 转义富文本内容
texteditor_content = texteditor_escape(input_content)
"""
import re

from enum import Enum
from adapter.common.log import logger
from adapter.common.pxfilter import XssHtml


def html_escape(html, is_json=False):
    """
    Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true, the quotation mark character (")
    is also translated.
    rewrite the cgi method
    @param html: html代码
    @param is_json: 是否为json串（True/False） ，默认为False
    """
    # &转换
    if not is_json:
        html = html.replace("&", "&amp;")  # Must be done first!
    # <>转换
    html = html.replace("<", "&lt;")
    html = html.replace(">", "&gt;")
    # 单双引号转换
    if not is_json:
        html = html.replace(" ", "&nbsp;")
        html = html.replace('"', "&quot;")
        html = html.replace("'", "&#39;")
    return html


def url_escape(url):
    url = url.replace("<", "")
    url = url.replace(">", "")
    url = url.replace(" ", "")
    url = url.replace('"', "")
    url = url.replace("'", "")
    return url


def texteditor_escape(str_escape):
    """
    富文本处理
    @param str_escape: 要检测的字符串
    """
    try:
        parser = XssHtml()
        parser.feed(str_escape)
        parser.close()
        return parser.get_html()
    except Exception as e: # pylint: disable=broad-except
        logger.exception("js脚本注入检测发生异常，错误信息：%s" % e)
        return str_escape


class ChoicesEnum(Enum):
    """
    常量枚举choices
    """

    @classmethod
    def get_choices(cls) -> tuple:
        """
        获取所有_choices_labels的tuple元组
        :return: tuple(tuple(key, value))
        """
        return cls._choices_labels.value

    @classmethod
    def get_choice_label(cls, key: str) -> dict:
        """
        获取_choices_labels的某个key值的value
        :param key: 获取choices的key值的value
        :return: str 字典value值
        """
        return dict(cls.get_choices()).get(key, key)

    @classmethod
    def get_dict_choices(cls) -> dict:
        """
        获取dict格式的choices字段
        :return: dict{key, value}
        """
        return dict(cls.get_choices())

    @classmethod
    def get_keys(cls) -> tuple:
        """
        获取所有_choices_keys的tuple元组(关联key值)
        :return: tuple(tuple(key, value))
        """
        return cls._choices_keys.value

    @classmethod
    def get_choice_key(cls, key: str) -> dict:
        """
        获取_choices_keys的某个key值的value
        :param key: 获取choices的key值的value
        :return: str 字典value值
        """
        return dict(cls.get_keys()).get(key, key)

    @classmethod
    def get_choices_list_dict(cls) -> list:
        """
        获取_choices_keys的某个key值的value
        :return: list[dict{id, name}]
        """
        return [{"id": key, "name": value} for key, value in cls.get_dict_choices().items()]


def is_match_variate(data):
    return re.compile("[a-zA-Z_]{1}[a-zA-Z0-9_]*").match(data)
