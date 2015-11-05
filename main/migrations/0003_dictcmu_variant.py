# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20151026_1849'),
    ]

    operations = [
        migrations.AddField(
            model_name='dictcmu',
            name='variant',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
