# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_auto_20140929_0130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='extract',
            name='provider',
        ),
    ]
