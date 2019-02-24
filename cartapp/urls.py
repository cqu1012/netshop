# -*- coding: utf-8 -*-
from django.conf.urls import url

from cartapp import views

urlpatterns = [
    url(r'^$', views.Addcart.as_view()),
    url(r'^queryAll/$', views.queryAll),
]