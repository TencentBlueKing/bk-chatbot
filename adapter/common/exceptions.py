# -*- coding: utf-8 -*-
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _


class ErrorCode(object):
    BKDOP_PLAT_CODE = "42"
    BKDOP_WEB_CODE = "00"


class BaseException(Exception):
    MODULE_CODE = "00"
    ERROR_CODE = "500"
    MESSAGE = _("系统异常")

    def __init__(self, *args, data=None, **kwargs):
        """
        @param {String} code 自动设置异常状态码
        """
        super(BaseException, self).__init__(*args)

        self.code = f"{ErrorCode.BKDOP_PLAT_CODE}{self.MODULE_CODE}{self.ERROR_CODE}"
        self.errors = kwargs.get("errors")

        # 优先使用第三方系统的错误编码
        if kwargs.get("code"):
            self.code = kwargs["code"]

        # 位置参数0是异常MESSAGE
        self.message = force_text(self.MESSAGE) if len(args) == 0 else force_text(args[0])

        # 当异常有进一步处理时，需返回data
        self.data = data

    def __str__(self):
        return "[{}] {}".format(self.code, self.message)


class ApiError(BaseException):
    pass


class ValidationError(BaseException):
    MESSAGE = _("参数验证失败")
    ERROR_CODE = "001"


class ApiResultError(ApiError):
    MESSAGE = _("远程服务请求结果异常")
    ERROR_CODE = "002"


class ComponentCallError(BaseException):
    MESSAGE = _("组件调用异常")
    ERROR_CODE = "003"


class BizNotExistError(BaseException):
    MESSAGE = _("业务不存在: {bk_biz_id}")
    ERROR_CODE = "004"


class LanguageDoseNotSupported(BaseException):
    MESSAGE = _("语言不支持")
    ERROR_CODE = "005"


class PermissionError(BaseException):
    MESSAGE = _("权限不足")
    ERROR_CODE = "403"


class ApiRequestError(ApiError):
    # 属于严重的场景，一般为第三方服务挂了，ESB调用超时
    MESSAGE = _("服务不稳定，请检查组件健康状况")
    ERROR_CODE = "015"
