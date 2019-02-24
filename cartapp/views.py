# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.views import View

from cartapp.cartmanager import getCartManger


class Addcart(View):
    def post(self,request):
        #让数据实时保存在session数据中
        request.session.modified = True
        flag = request.POST.get('flag','')
        cartManager = getCartManger(request)
        #添加至购物车
        if flag == 'add':
            # cartItem = request.POST.dict()
            # cartItem.pop('flag')
            cartManager.add(**request.POST.dict())
        #增加操作
        if flag == 'plus':
            cartManager.update(step=1,**request.POST.dict())
        #减少操作
        if flag == 'minus':
            cartManager.update(step=-1,**request.POST.dict())
        if flag == 'delete':
            cartManager.delete(**request.POST.dict())
        return HttpResponseRedirect('/cart/queryAll/')


def queryAll(request):
    cartManager = getCartManger(request)
    cartList = cartManager.queryAll()
    return render(request,'cart.html',{'cartList':cartList})


