# -*- coding: utf-8 -*-
"""
时间处理模块
"""
import datetime
import time
import pytz

from django.utils import timezone
from rest_framework import serializers

# 默认时间戳乘数
DEFAULT_MULTIPLICATOR = 1
# dtEventTimeStamp时间戳乘数
DTEVENTTIMESTAMP_MULTIPLICATOR = 1000
# INFLUXDB时间戳乘数
INFLUXDB_MULTIPLICATOR = 1000000000

# 一周时间
WEEK_DELTA_TIME = 7 * 24 * 60 * 60
DAY = 86400

SHOW_TZ = False
FMT_LENGTH = None if SHOW_TZ else 16


def timeformat_to_timestamp(timeformat, time_multiplicator=DEFAULT_MULTIPLICATOR):
    """
    时间格式 -> 时间戳
    :param timeformat:
    :param time_multiplicator: 时间倍数
    :return:
    """
    if not timeformat:
        return None
    if type(timeformat) in [str]:
        # 时间字符串转时间戳
        timestamp = int(time.mktime(time.strptime(timeformat, "%Y-%m-%d %H:%M:%S")))
    else:
        # type(timeformat) is datetime
        # datetime 转时间戳
        timestamp = int(timeformat.strftime("%s"))
    return int(timestamp * time_multiplicator)


def timestamp_to_datetime(from_timestamp, time_multiplicator=DEFAULT_MULTIPLICATOR):
    """
    timestamp -> aware datetime
    """
    utc_tz = pytz.timezone("UTC")
    utc_dt = utc_tz.localize(datetime.datetime.utcfromtimestamp(int(from_timestamp) / time_multiplicator))
    return utc_dt


def generate_influxdb_time_range(start_timestamp, end_timestamp):
    """
    生成influxdb需要的时间段
    """
    if end_timestamp > time.time():
        end_timestamp = time.time()
    if start_timestamp < time.time() - DAY * 30:
        start_timestamp = time.time() - DAY * 30
    return int(start_timestamp) * INFLUXDB_MULTIPLICATOR, int(end_timestamp) * INFLUXDB_MULTIPLICATOR


def time_format(l_time, is_tz=False):
    """
    把时间戳列表根据时间间隔转为转为可读的时间格式
    @param {datetime} l_time 时间戳列表
    @param {Boolean} is_tz 是否显示时区
    """
    if l_time:
        difference = l_time[-1] - l_time[0]
        count = len(l_time)
        if count > 1:
            frequency = difference / (count - 1)
            if difference < DAY and frequency < DAY:
                start = 11
                end = None if is_tz else FMT_LENGTH
            elif frequency < DAY <= difference:
                start = 5
                end = None if is_tz else FMT_LENGTH
            elif difference >= DAY and frequency >= DAY:
                start = 5
                end = 10
            else:
                start = None
                end = None if is_tz else FMT_LENGTH
            formated_time = [timestamp_to_timeformat(t)[start:end] for t in l_time]
        else:
            formated_time = [timestamp_to_timeformat(l_time[0])]
    else:
        formated_time = []
    return formated_time


def format_datetime(o_datetime):
    """
    格式化日志对象展示格式

    @param {datetime} o_dateitime
    """
    return o_datetime.strftime("%Y-%m-%d %H:%M:%S%z")


def get_active_timezone_offset():
    """
    获取当前用户时区偏移量
    """
    tz = str(timezone.get_current_timezone())
    offset = datetime.datetime.now(pytz.timezone(tz)).strftime("%z")
    return offset


def strftime_local(aware_time, fmt="%Y-%m-%d %H:%M:%S"):
    """
    格式化aware_time为本地时间
    """
    if not aware_time:
        # 当时间字段允许为NULL时，直接返回None
        return None
    if timezone.is_aware(aware_time):
        # translate to time in local timezone
        aware_time = timezone.localtime(aware_time)
    return aware_time.strftime(fmt)


def localtime_to_timezone(d_time, to_zone):
    """
    将时间字符串根据源时区转为用户时区
    @param {datetime} d_time 时间
    @param {String} to_zone 时区
    """
    zone = pytz.timezone(to_zone)
    return d_time.astimezone(zone)


class SelfDRFDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if not value:
            return None
        return strftime_local(value)


def time_to_string(t):
    """
    传入一个标准时间，返回其字符串形式
    :param t: 时间
    :return: 时间字符串
    """
    return t.strftime("%Y-%m-%d %H:%M:%S")


def date_to_string(d):
    """
    传入一个标准日期，返回其字符串形式
    :param d: 日期
    :return: 日期字符串
    """
    return d.strftime("%Y-%m-%d")


def string_to_time(t_str):
    """
    传入一个字符串，返回其标准时间格式
    :param t_str: 时间字符串
    :return: 时间
    """
    return datetime.datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")


def string_to_date(d_str):
    """
    传入一个字符串，返回其标准日期格式
    :param d_str: 日期字符串
    :return: 日期
    """
    return datetime.datetime.strptime(d_str, "%Y-%m-%d")
