# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20151117_0653'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dictcmu',
            name='deseret',
        ),
        migrations.AddField(
            model_name='dictcmu',
            name='source',
            field=models.CharField(max_length=25, null=True, blank=True),
        ),
    ]
