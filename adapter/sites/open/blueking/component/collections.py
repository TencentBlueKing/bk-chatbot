# -*- coding: utf-8 -*-
"""Collections for component client"""
from .apis.bk_login import CollectionsBkLogin
from .apis.bk_paas import CollectionsBkPaas
from .apis.cc import CollectionsCC
from .apis.cmsi import CollectionsCMSI
from .apis.gse import CollectionsGSE
from .apis.job import CollectionsJOB
from .apis.jobv3 import CollectionsJOBV3
from .apis.sops import CollectionsSOPS
from .apis.esb import CollectionsEsb


# Available components
AVAILABLE_COLLECTIONS = {
    'bk_login': CollectionsBkLogin,
    'bk_paas': CollectionsBkPaas,
    'cc': CollectionsCC,
    'cmsi': CollectionsCMSI,
    'gse': CollectionsGSE,
    'job': CollectionsJOB,
    'jobv3': CollectionsJOBV3,
    'sops': CollectionsSOPS,
    'esb': CollectionsEsb,
}
