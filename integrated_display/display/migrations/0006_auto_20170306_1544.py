# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-06 07:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('display', '0005_platform_summary_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='platform_summary_day',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]