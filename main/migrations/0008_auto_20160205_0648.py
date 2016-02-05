# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20160204_1339'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dictcmu',
            old_name='variant',
            new_name='num_of_variants',
        ),
        migrations.AddField(
            model_name='dictcmu',
            name='variant_num',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
