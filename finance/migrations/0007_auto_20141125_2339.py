# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_auto_20141125_0121'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='WeekDay',
            new_name='WeekNumber',
        ),
    ]
