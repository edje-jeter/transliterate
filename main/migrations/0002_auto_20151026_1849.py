# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dictcmu',
            old_name='length',
            new_name='char_length',
        ),
        migrations.AddField(
            model_name='dictcmu',
            name='list_length',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
