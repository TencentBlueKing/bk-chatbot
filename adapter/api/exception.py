# -*- coding: utf-8 -*-
from django.utils.encoding import force_text


class DataBaseException(Exception):
    pass


class DataAPIException(DataBaseException):
    """Exception for Component API"""

    def __init__(self, api_obj, error_message, response=None):
        self.api_obj = api_obj
        self.error_message = force_text(error_message)
        self.response = response

        if self.response is not None:
            error_message = "{}, resp={}".format(error_message, self.response)

        super(DataAPIException, self).__init__(error_message)
