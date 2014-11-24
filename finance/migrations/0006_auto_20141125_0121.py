# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_comment_pendingemail_talk_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeekDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('num_week', models.IntegerField()),
                ('date_init', models.DateField(verbose_name='date initial week')),
                ('date_final', models.DateField(verbose_name='date final week')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.DeleteModel(
            name='PendingEmail',
        ),
        migrations.DeleteModel(
            name='Talk',
        ),
        migrations.DeleteModel(
            name='User',
        ),
        migrations.AddField(
            model_name='provider',
            name='num_week',
            field=models.ForeignKey(blank=True, null=True, to='finance.WeekDay'),
            preserve_default=True,
        ),
    ]
