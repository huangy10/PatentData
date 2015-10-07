# coding=utf-8
from django.db import models
# Create your models here.


class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name='公司名称')
    checked = models.BooleanField(default=False)


class Patent(models.Model):
    name = models.CharField(max_length=255, verbose_name='专利名称')
    apply_at = models.DateField(verbose_name='申请日期')
    note = models.CharField(max_length=100, verbose_name='专利号', unique=True)
    abstract = models.CharField(max_length=255, verbose_name='摘要')
    category = models.CharField(max_length=20, verbose_name='主分类号')
    company = models.ForeignKey(Company, verbose_name='申请公司')
    type = models.CharField(choices=(
        ('FM', '发明'),
        ('SY', '实用'),
        ('WG', '外观'),
    ), verbose_name='专利种类', max_length=2)
    status = models.CharField(choices=(
        ('valid', '有权'),
        ('applying', '申请中'),
        ('invalid', '无权'),
    ), max_length=10, verbose_name='专利状态')
