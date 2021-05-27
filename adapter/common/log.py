# -*- coding: utf-8 -*-

"""
Usage:

    from apps.common.log import logger

    logger.info("test")
    logger.error("wrong1")
    logger.exception("wrong2")

    # with traceback
    try:
        1 / 0
    except Exception:
        logger.exception("wrong3")
"""
import logging

from adapter.utils.local import get_request_id

logger_detail = logging.getLogger("root")


# ===============================================================================
# 自定义添加打印内容
# ===============================================================================
# traceback--打印详细错误日志
class logger_traceback:
    """
    详细异常信息追踪
    """

    def __init__(self):
        pass

    def error(self, message=""):
        """
        打印 error 日志方法
        """
        message = self.build_message(message)
        logger_detail.error(message)

    def info(self, message=""):
        """
        info 日志
        """
        message = self.build_message(message)
        # logger_detail.info(message)

    def warning(self, message=""):
        """
        warning 日志
        """
        message = self.build_message(message)
        logger_detail.warning(message)

    def debug(self, message=""):
        """
        debug 日志
        """
        message = self.build_message(message)
        logger_detail.debug(message)

    def critical(self, message=""):
        """
        critical 日志
        """
        message = self.build_message(message)
        logger_detail.critical(message)

    def exception(self, message="", *args):
        message = self.build_message(message)
        logger_detail.exception(message, *args)

    @staticmethod
    def build_message(message):
        request_id = get_request_id()
        return "{} | {}".format(request_id, message)


# traceback--打印详细错误日志
logger = logger_traceback()
