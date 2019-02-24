# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import math

from django.db import models
from userapp.models import *
from goodsapp.models import *
# Create your models here.
#goodsid="5" sizeid="17" colorid="17"
class Cartitem(models.Model):
    goodsid = models.PositiveIntegerField()
    colorid = models.PositiveIntegerField()
    sizeid = models.PositiveIntegerField()
    count = models.PositiveIntegerField()
    isdelete = models.BooleanField(default=False)
    user = models.ForeignKey(UserInfo)
    def getGoods(self):
        return Goods.objects.get(id=self.goodsid)
    def getColor(self):
        return Color.objects.get(id=self.colorid)
    def getSize(self):
        return Size.objects.get(id=self.sizeid)
    def getTotalPrice(self):
        return math.ceil(int(self.count) * self.getGoods().price)

