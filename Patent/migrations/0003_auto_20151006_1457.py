# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Patent', '0002_remove_company_original_row_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='checked',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='patent',
            name='note',
            field=models.CharField(unique=True, max_length=100, verbose_name=b'\xe4\xb8\x93\xe5\x88\xa9\xe5\x8f\xb7'),
        ),
        migrations.AlterField(
            model_name='patent',
            name='status',
            field=models.CharField(max_length=10, verbose_name=b'\xe4\xb8\x93\xe5\x88\xa9\xe7\x8a\xb6\xe6\x80\x81', choices=[(b'valid', b'\xe6\x9c\x89\xe6\x9d\x83'), (b'applying', b'\xe7\x94\xb3\xe8\xaf\xb7\xe4\xb8\xad'), (b'invalid', b'\xe6\x97\xa0\xe6\x9d\x83')]),
        ),
    ]
