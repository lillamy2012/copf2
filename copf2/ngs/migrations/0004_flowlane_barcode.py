# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-13 08:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ngs', '0003_auto_20160413_0636'),
    ]

    operations = [
        migrations.AddField(
            model_name='flowlane',
            name='barcode',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
