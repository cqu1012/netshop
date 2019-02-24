# -*- coding: utf-8 -*-
from django.conf.urls import url

from orderapp import views

urlpatterns = [
    url(r'^$',views.OderView.as_view()),
    url(r'^toOrder/', views.toOrderView),
    url(r'^toPay/', views.ViewToPay.as_view()),
    url(r'^checkPay/', views.CheckPay.as_view()),
]