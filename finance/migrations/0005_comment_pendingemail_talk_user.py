# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import flask_login


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0004_remove_extract_provider'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('body', models.CharField(max_length=100)),
                ('body_html', models.CharField(max_length=100)),
                ('timestamp', models.DateField(verbose_name='date last purchase')),
                ('author_id', models.DecimalField(decimal_places=2, max_digits=8)),
                ('author_name', models.CharField(max_length=100)),
                ('author_email', models.CharField(max_length=100)),
                ('notify', models.BooleanField(db_index=True, default=True)),
                ('approved', models.BooleanField(db_index=True, default=True)),
                ('talk_id', models.DecimalField(decimal_places=2, max_digits=8)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PendingEmail',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('subject', models.CharField(max_length=100)),
                ('body_text', models.CharField(max_length=100)),
                ('body_html', models.CharField(max_length=100)),
                ('talk_id', models.DecimalField(decimal_places=2, max_digits=8)),
                ('timestamp', models.DateField(verbose_name='date last purchase')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Talk',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('slides', models.CharField(max_length=100)),
                ('video', models.CharField(max_length=100)),
                ('user_id', models.DecimalField(decimal_places=2, max_digits=8)),
                ('venue', models.CharField(max_length=100)),
                ('venue_url', models.CharField(max_length=100)),
                ('date', models.DateField(verbose_name='date last purchase')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('email', models.CharField(max_length=100)),
                ('username', models.CharField(max_length=100)),
                ('is_admin', models.BooleanField(db_index=True, default=True)),
                ('password_hash', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('bio', models.CharField(max_length=100)),
                ('member_since', models.DateField(verbose_name='date last purchase')),
                ('avatar_hash', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(flask_login.UserMixin, models.Model),
        ),
    ]
