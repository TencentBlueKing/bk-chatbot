# -*- coding: utf-8 -*-
from dogpile.cache import make_region

cache_dict = {}
region = make_region().configure("dogpile.cache.memory", arguments={"cache_dict": cache_dict})
