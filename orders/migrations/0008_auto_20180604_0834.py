# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-04 05:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_order_pageid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='name',
            field=models.CharField(max_length=120, null=True, verbose_name='Фамилия Имя Отчество'),
        ),
    ]
