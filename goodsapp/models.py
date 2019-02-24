# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import collections
# Create your models here.
class Category(models.Model):
    cname = models.CharField(max_length=10)
    def __unicode__(self):
        return '<Category>:%s'%self.cname

class Goods(models.Model):
    gname = models.CharField(max_length=100,unique=True)
    gdesc = models.CharField(max_length=100)
    oldprice = models.DecimalField(max_digits=5,decimal_places=2)
    price = models.DecimalField(max_digits=5,decimal_places=2)
    category =models.ForeignKey(Category)
    def __unicode__(self):
        return '<Goods>:%s'%self.gname
    def getColorImg(self):
        return self.inventory_set.first().color.colorurl
    def getColors(self):
        colors = []
        for inventory in self.inventory_set.all():
            color = inventory.color
            if color not in colors:
                colors.append(color)
        return colors
    def getSize(self):
        sizes = []
        for inventory in self.inventory_set.all():
            size = inventory.size
            if size not in sizes:
                sizes.append(size)
        return sizes
    def getDetailImg(self):
        datas = collections.OrderedDict()
        #遍历当前商品中的所有详细图片
        for goodsdetail in self.goodsdetail_set.all():
            detailName = goodsdetail.getName()
            if not datas.has_key(detailName):
                datas[detailName]=[goodsdetail.gdurl]
            else:
                datas[detailName].append(goodsdetail.gdurl)
        return datas



class Goodsdetailname(models.Model):
    gdname =models.CharField(max_length=30)

class Goodsdetail(models.Model):
    gdurl = models.ImageField(upload_to='')
    gdname = models.ForeignKey(Goodsdetailname)
    goods = models.ForeignKey(Goods)
    def getName(self):
        return self.gdname.gdname

class Size(models.Model):
    sname = models.CharField(max_length=10)

class Color(models.Model):
    colorname = models.CharField(max_length=10)
    colorurl = models.ImageField(upload_to='color/')


class Inventory(models.Model):
    count =models.PositiveIntegerField()
    color = models.ForeignKey(Color)
    goods = models.ForeignKey(Goods)
    size = models.ForeignKey(Size)

