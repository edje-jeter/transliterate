# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_dictcmu_deseret'),
    ]

    operations = [
        migrations.AddField(
            model_name='dictcmu',
            name='phonemes_no_num',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
