# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-12 02:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0010_homeworkattachment'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='homeworkattachment',
            unique_together=set([('attachment_url',)]),
        ),
    ]