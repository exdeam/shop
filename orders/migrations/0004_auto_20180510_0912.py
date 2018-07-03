# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-10 09:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_shipping_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='shipping_method',
            field=models.CharField(blank=True, default=1, max_length=120, verbose_name='Доставка'),
            preserve_default=False,
        ),
    ]
