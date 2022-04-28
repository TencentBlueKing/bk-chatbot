# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group


class AppModelAdmin(admin.ModelAdmin):
    """
    admin基础类
    """

    save_as = True


# 隐藏不需要查看的模块
admin.site.unregister(Group)
admin.site.unregister(Site)
