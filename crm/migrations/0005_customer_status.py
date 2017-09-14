# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-02 14:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_userprofile_roles'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='status',
            field=models.SmallIntegerField(choices=[(0, '未报名'), (1, '已报名')], default=0, verbose_name='报名状态'),
        ),
    ]