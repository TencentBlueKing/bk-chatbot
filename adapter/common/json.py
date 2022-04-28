# -*- coding: utf-8 -*-
import uuid
import decimal
import datetime
import json
from django.utils.timezone import is_aware
from django.utils.duration import duration_iso_string
from django.utils import six
from django.utils.deprecation import CallableBool
from django.utils.functional import Promise
from adapter.utils.time_handler import date_to_string, strftime_local


class DjangoJSONEncoderExtend(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal types and UUIDs.
    """

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            return strftime_local(o, fmt="%Y-%m-%d %H:%M:%S%z")
        elif isinstance(o, datetime.date):
            return date_to_string(o)
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        elif isinstance(o, uuid.UUID) or isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, Promise):
            return six.text_type(o)
        elif isinstance(o, CallableBool):
            return bool(o)
        elif isinstance(o, set):
            return list(o)
        else:
            return super(DjangoJSONEncoderExtend, self).default(o)
