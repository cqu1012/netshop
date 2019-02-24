# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import F
from django.db.transaction import atomic
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import jsonpickle

# Create your views here.
from django.views import View

from cartapp.cartmanager import getCartManger
from goodsapp.models import Inventory
from orderapp.models import Order, OrderItem
from userapp.models import Address
from utils.alipay import AliPay


class OderView(View):
    def get(self,request):
        user = request.session.get('user','')
        cartitems = request.GET.get('cartitems','')
        if user:
            return HttpResponseRedirect('/order/toOrder/?cartitems='+cartitems)
        return HttpResponseRedirect('/user/login/?redirct=order&cartitems='+cartitems)

def toOrderView(request):
    #获取购物车商品对象
    cartitems = request.GET.get('cartitems','')
    cartitemsList = jsonpickle.loads(cartitems)
    cartitemsObjList = [getCartManger(request).get_cartitems(**ci) for ci in cartitemsList if ci]
    #获取用户地址
    user = jsonpickle.loads(request.session.get('user',''))
    addr = user.address_set.get(isdefault=True)
    #获取商品总金额
    totalPrice = 0
    # print(cartitems)
    for cartitem in cartitemsObjList:
        totalPrice += cartitem.getTotalPrice()


    return render(request,'order.html',{'cartitemsObjList':cartitemsObjList,'addr':addr,'totalPrice':totalPrice})
#创建Alipay对象
alipay = AliPay(appid='2016092500589718', app_notify_url='http://127.0.0.1:8000/order/checkPay/', app_private_key_path='orderapp/keys/my_private_key.txt',
                 alipay_public_key_path='orderapp/keys/alipay_public_key.txt', return_url='http://127.0.0.1:8000/order/checkPay/', debug=True)

import jsonpickle
class ViewToPay(View):
    # @atomic
    def get(self,request):
        #获得购物车项目
        cartitemsList = jsonpickle.loads(request.GET.get('cartitems',''))
        addrID = request.GET.get('address','-1')
        addrID = int(addrID)
        addrObj = Address.objects.get(id = addrID)
        payway = request.GET.get('payway','')

        #添加Order表信息
        import uuid
        import datetime
        raw_order = {
            'out_trade_num':uuid.uuid4().get_hex(),
            'order_num':datetime.datetime.today().strftime('%Y%m%d%H%M%S'),
            'payway':payway,
            'address':addrObj,
            'user':jsonpickle.loads(request.session.get('user',''))

        }

        ''' 
            out_trade_num = models.UUIDField()
            order_num = models.CharField(max_length=50)
            trade_no = models.CharField(max_length=120,default='')
            status = models.CharField(max_length=20,default=u'待支付')
            payway = models.CharField(max_length=20,default='alipay')
            address = models.ForeignKey(Address)
            user = models.ForeignKey(UserInfo)
        '''
        print(raw_order)
        orderObj = Order.objects.create(**raw_order)

        #添加OrderItems表信息
        orderItemsList = [OrderItem.objects.create(order=orderObj,**ci) for ci in cartitemsList if ci]
        #获取支付总金额
        totalPrice = request.GET.get('totalPrice','')
        aliapayParams = alipay.direct_pay(subject=u'万家百货', out_trade_no=orderObj.out_trade_num, total_amount=totalPrice)
        #网址？传递的参数格式
        url = alipay.gateway+'?'+aliapayParams

        return HttpResponseRedirect(url)


class CheckPay(View):
    def get(self,request):
        #获取请求参数
        params = request.GET.dict()
        print(params)
        #获取签名
        sign = params.pop('sign')
        '''
        {
            u'trade_no': u'2019021722001432400500409435',
            u'seller_id': u'2088102177140935',
            u'total_amount': u'223.00',
            u'timestamp': u'2019-02-1711: 01: 52',
            u'charset': u'utf-8',
            u'app_id': u'2016092500589718',
            u'sign': u'F43sZnaNaqtnptk80pXw2YYEOKUfYnh5RddW1h22S5nTEE3RzjLUB4r1QMhjtJGYEO9/BVrRYHL/peN0dzrT5eq/Swp03lN5mE7W7WN4bFvUgJgBRaBlcuTzZ02IBofUG2SNsDTm+vdl8TyUbkrIl2x7PTOiWsSv4s5u1yrhPjDCBFrvfshSVW0Qs+89dKQSgh4FqNnBEmZO0fYeOkGExTd/CcRNqrSqnNloyV+0PDrfYehUJII5y6vXLi4AgJXKnoFpNERBNiiSBYIvg7YXVaeIqu7LW7D8MtFz2m1U2FMjsvemMwrWLMxW83XQkbk9xPn2G6h9F7z+sn9hyRVIYQ==',
            u'out_trade_no': u'b91eee7ab96745ce8eb0310c1d56e4e9',
            u'version': u'1.0',
            u'sign_type': u'RSA2',
            u'auth_app_id': u'2016092500589718',
            u'method': u'alipay.trade.page.pay.return'
        }
        '''
        #判断是否支付成功
        if alipay.verify(params,sign):
            #修改订单信息‘待支付’--->‘待发货’
            outTradeNo = params.get('out_trade_no')
            order = Order.objects.get(out_trade_num=outTradeNo)
            # order.status = u'待发货'
            Order.objects.filter(out_trade_num=outTradeNo).update(status=u'待发货')
            #减少库存
            [Inventory.objects.filter(color=oi.colorid,goods=oi.goodsid,size=oi.sizeid).update(count=F('count')-oi.count) for oi in order.orderitem_set.all() if oi]
            #清空购物车
            user = jsonpickle.loads(request.session.get('user',''))
            [user.cartitem_set.filter(colorid=oi.colorid,goodsid=oi.goodsid,sizeid=oi.sizeid).delete() for oi in order.orderitem_set.all() if oi]

            return HttpResponse('支付成功！')
        return HttpResponse('支付失败！')
