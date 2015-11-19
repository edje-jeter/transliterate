# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_dictcmu_phonemes_no_num'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dictcmu',
            name='entry',
            field=models.CharField(db_index=True, max_length=255, null=True, blank=True),
        ),
    ]
