# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'\xe5\x85\xac\xe5\x8f\xb8\xe5\x90\x8d\xe7\xa7\xb0')),
                ('original_row_index', models.IntegerField(verbose_name=b'\xe5\x9c\xa8\xe5\x8e\x9fexcel\xe8\xa1\xa8\xe4\xb8\xad\xe7\x9a\x84\xe8\xa1\x8c\xe6\xa0\x87')),
            ],
        ),
        migrations.CreateModel(
            name='Patent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'\xe4\xb8\x93\xe5\x88\xa9\xe5\x90\x8d\xe7\xa7\xb0')),
                ('apply_at', models.DateField(verbose_name=b'\xe7\x94\xb3\xe8\xaf\xb7\xe6\x97\xa5\xe6\x9c\x9f')),
                ('note', models.CharField(max_length=100, verbose_name=b'\xe4\xb8\x93\xe5\x88\xa9\xe5\x8f\xb7')),
                ('abstract', models.CharField(max_length=255, verbose_name=b'\xe6\x91\x98\xe8\xa6\x81')),
                ('category', models.CharField(max_length=20, verbose_name=b'\xe4\xb8\xbb\xe5\x88\x86\xe7\xb1\xbb\xe5\x8f\xb7')),
                ('type', models.CharField(max_length=2, verbose_name=b'\xe4\xb8\x93\xe5\x88\xa9\xe7\xa7\x8d\xe7\xb1\xbb', choices=[(b'FM', b'\xe5\x8f\x91\xe6\x98\x8e'), (b'SY', b'\xe5\xae\x9e\xe7\x94\xa8'), (b'WG', b'\xe5\xa4\x96\xe8\xa7\x82')])),
                ('status', models.CharField(max_length=10, verbose_name=b'\xe4\xb8\x93\xe5\x88\xa9\xe7\x8a\xb6\xe6\x80\x81', choices=[(b'in_use', b'\xe6\x9c\x89\xe6\x9d\x83'), (b'applying', b'\xe7\x94\xb3\xe8\xaf\xb7\xe4\xb8\xad'), (b'dropped', b'\xe6\x97\xa0\xe6\x9d\x83')])),
                ('company', models.ForeignKey(verbose_name=b'\xe7\x94\xb3\xe8\xaf\xb7\xe5\x85\xac\xe5\x8f\xb8', to='Patent.Company')),
            ],
        ),
    ]
