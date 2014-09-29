# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_auto_20140928_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extract',
            name='value_balance',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
        migrations.AlterField(
            model_name='extract',
            name='value_credit',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
        migrations.AlterField(
            model_name='extract',
            name='value_debit',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
        migrations.AlterField(
            model_name='provider',
            name='value_total',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
    ]
