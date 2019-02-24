# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math

from django.core.paginator import Paginator
from django.shortcuts import render

from .models import *

# Create your views here.
# def indexView(request):
#     return render(request,'index.html')
from django.views import View
class IndexView(View):
    def get(self,request,cid=2,num=1):
        cid = int(cid)
        num = int(num)
        #返回所有类别信息
        categorylist=Category.objects.all()
        #返回类别下的所有商品信息
        goodslist = Goods.objects.filter(category=cid).order_by('id')

        # 创建分页器对象
        page_obj = Paginator(goodslist,8)
        # 获取页数据
        page_post = page_obj.page(num)
        # 获取每一页显示的码数数列表
        begin = num - int(math.ceil(10.0 / 2))
        if begin < 1:
            begin = 1
        end = begin + 9
        if end > page_obj.num_pages:
            end = page_obj.num_pages
        if end < 10:
            begin = 1
        else:
            begin = end - 9
        pagelist = range(begin, end + 1)
        # 'postlist':page_post, 'pagelist':pagelist, 'currentNum':num
        return render(request,'index.html',{'categorylist':categorylist,'cid':cid,'goodslist':page_post,'pagelist':pagelist,'currentNum':num})
def recommend_view(func):
    def _wrapper(detailView,request,goodsId,*args,**kwags):
        #从cookie中获取用户访问的goodid字符串
        c_goodidStr = request.COOKIES.get('recommend','')

        #存放goodid的列表 ['1','2','3'] ==>'1 2'
        goodsIdList = [gid for gid in c_goodidStr.split( ) if gid.strip()]

        #存放推荐商品对象的列表
        goodsObjList = [Goods.objects.get(id = ggid) for ggid in goodsIdList if ggid != goodsId and Goods.objects.get(id=ggid).category_id == Goods.objects.get(id = goodsId).category_id][:4]

        #将推荐商品列表传递给func函数
        response = func(detailView,request,goodsId,goodsObjList,*args,**kwags)

        #判断用户访问的商品是否已存在goodsIdList中
        if goodsId in goodsIdList:
            goodsIdList.remove(goodsId)
            goodsIdList.insert(0,goodsId)
        else:
            goodsIdList.insert(0,goodsId)

        #将用户每次访问的商品ID存放在cookie中
        response.set_cookie('recommend',' '.join(goodsIdList),max_age = 3*24*60*60)
        return response
    return _wrapper

class GoodsDetailView(View):
    @recommend_view
    def get(self,request,goodsId,recommend_list=[]):
        goodsId = int(goodsId)
        # 获取当前商品
        goods = Goods.objects.get(id=goodsId)
        return render(request,'detail.html',{'goods':goods,'recommend_list':recommend_list})