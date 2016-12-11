# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^daystat/$', admin.site.admin_view(views.DealStatView.as_view()), name='daystat'),
]