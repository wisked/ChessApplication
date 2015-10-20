# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('ello_rate', models.FloatField(default=0)),
            ],
            options={
                'ordering': ['ello_rate'],
                'db_table': '',
            },
        ),
        migrations.CreateModel(
            name='RegisterPlayer',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('ello_rate', models.FloatField(default=0)),
                ('result', models.FloatField(choices=[(1, 'Победа'), (0.5, 'Ничья'), (0, 'Проигрыш')])),
                ('table_id', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'register',
            },
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('number', models.PositiveIntegerField()),
            ],
            options={
                'db_table': 'rounds',
            },
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('number_table', models.PositiveIntegerField()),
                ('round_id', models.ForeignKey(to='chess.Round')),
            ],
            options={
                'db_table': 'tables',
            },
        ),
        migrations.AddField(
            model_name='player',
            name='table',
            field=models.ForeignKey(to='chess.Table'),
        ),
    ]
