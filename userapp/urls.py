# -*- coding: utf-8 -*-
from django.conf.urls import url

from userapp import views

urlpatterns = [
    url(r'^register/$',views.UserRegister.as_view()),
    url(r'^center/$',views.UserCenter.as_view()),
    url(r'^login/$',views.UserLogin.as_view()),
    url(r'^codeImg/$',views.CodeImg.as_view()),
    url(r'^checkcode/$',views.CheckCode.as_view()),
    url(r'^logout/$',views.LogOut.as_view()),
    url(r'^address/$',views.UserAddress.as_view()),
    url(r'^getaddress/$',views.getAddress),
]