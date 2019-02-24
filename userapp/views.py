# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from cartapp.cartmanager import SessionCartManager
from .models import *

import jsonpickle


class UserRegister(View):
    def get(self,request):
        return render(request, 'register.html')
    def post(self,request):
        account = request.POST.get('account','')
        password = request.POST.get('password','')
        user = UserInfo.objects.create(uname=account,pwd=password)
        if user:
            #将当前用户的信息保存到session中
            request.session['user'] = jsonpickle.dumps(user)
            return HttpResponseRedirect('/user/center/')
        return HttpResponseRedirect('/user/register/')

class UserCenter(View):
    def get(self,request):
        return render(request,'center.html')


class UserLogin(View):
    def get(self,request):
        red = request.GET.get('redirct','')
        return render(request,'login.html',{'red':red,'cartitems':request.GET.get('cartitems','')})
    def post(self,request):
        uname = request.POST.get('account','')
        pwd = request.POST.get('password','')
        red = request.POST.get('redirect','')
        userList = UserInfo.objects.filter(uname = uname,pwd = pwd)
        if userList:
            request.session['user'] = jsonpickle.dumps(userList[0])
            if red == 'cart':
                #将session中的购物项转移到数据库表中
                SessionCartManager(request.session).migrateSession2DB()
                return HttpResponseRedirect('/cart/queryAll/')
            elif red == 'order':
                cartitems = request.POST.get('cartitems','')
                return HttpResponseRedirect('/order/toOrder/?cartitems=' + cartitems)
            return HttpResponseRedirect('/user/center/')
        return HttpResponseRedirect('/user/login/')

from utils.code import *
class CodeImg(View):
    def get(self,request):
        img,txt = gene_code()
        request.session['codetxt']=txt
        return  HttpResponse(img,content_type='image/png')


class CheckCode(View):
    def get(self,request):
        #用户输入code
        inpCode = request.GET.get('code','')
        #实际生成code
        CreCode = request.session.get('codetxt','')

        flag = inpCode==CreCode
        return JsonResponse({'flag':flag})


class LogOut(View):
    def get(self,request):
        #清空session数据
        request.session.clear()
        return JsonResponse({'flag':True})


class UserAddress(View):
    def get(self,request):
        user = jsonpickle.loads(request.session.get('user',''))
        addrList = user.address_set.all()
        return render(request, 'address.html',{'addrList':addrList})
    def post(self,request):
        #把post请求转换成字典格式
        userAddr = request.POST.dict()
        #去除CSRF字典中的值
        userAddr.pop('csrfmiddlewaretoken')
        #获取user信息
        user = jsonpickle.loads(request.session.get('user',''))
        #写入到数据库中
        try:
            Address.objects.create(userinfo=user,isdefault=(lambda count:True if count==0 else False)(user.address_set.count()),**userAddr)
        except Exception as e:
            print(e.args)
        return HttpResponseRedirect('/user/address/')

def getAddress(request):
    pid = request.GET.get('pid', -1)
    pid = int(pid)
    arealist = Area.objects.filter(parentid=pid)
    jarealist = serializers.serialize('json', arealist)
    return JsonResponse({'jarealist': jarealist})