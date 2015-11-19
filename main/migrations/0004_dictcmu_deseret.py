# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_dictcmu_variant'),
    ]

    operations = [
        migrations.AddField(
            model_name='dictcmu',
            name='deseret',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
