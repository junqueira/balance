# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extract',
            name='date_launch',
            field=models.DateField(verbose_name='date launch'),
        ),
        migrations.AlterField(
            model_name='extract',
            name='date_purchase',
            field=models.DateField(verbose_name='date purchase'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='date_last_purchase',
            field=models.DateField(verbose_name='date last purchase'),
        ),
    ]
