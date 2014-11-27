# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0007_auto_20141125_2339'),
    ]

    operations = [
        migrations.RenameField(
            model_name='provider',
            old_name='value_total',
            new_name='total_debit_week',
        ),
        migrations.AddField(
            model_name='provider',
            name='total_credit_week',
            field=models.DecimalField(default=0, decimal_places=2, max_digits=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='typelaunch',
            name='cost_fixo',
            field=models.BooleanField(db_index=True, default=False),
            preserve_default=True,
        ),
    ]
