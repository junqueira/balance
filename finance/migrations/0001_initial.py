# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Extract',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('date_launch', models.DateTimeField(verbose_name='date launch')),
                ('launch', models.CharField(max_length=100)),
                ('date_purchase', models.DateTimeField(verbose_name='date purchase')),
                ('value_debit', models.DecimalField(max_digits=5, decimal_places=2)),
                ('value_credit', models.DecimalField(max_digits=5, decimal_places=2)),
                ('value_balance', models.DecimalField(max_digits=5, decimal_places=2)),
                ('cancelled', models.BooleanField(db_index=True, default=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('description', models.CharField(unique=True, max_length=100)),
                ('date_last_purchase', models.DateTimeField(verbose_name='date last purchase')),
                ('value_total', models.DecimalField(max_digits=5, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TypeLaunch',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('type_name', models.CharField(unique=True, max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='provider',
            name='type_launch',
            field=models.ForeignKey(null=True, blank=True, to='finance.TypeLaunch'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='extract',
            name='provider',
            field=models.ForeignKey(null=True, blank=True, to='finance.Provider'),
            preserve_default=True,
        ),
    ]
