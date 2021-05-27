# -*- coding: utf-8 -*-
from .default import *  # noqa

BKDATA_URL = f"{os.getenv('BK_PAAS_HOST', '')}/t/bk_dataweb"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'xxx',
        'USER': 'xxx',
        'PASSWORD': 'xxx',
        'HOST': 'xxxx',
        'PORT': 'xxxx',
    },
}

