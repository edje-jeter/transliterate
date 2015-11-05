# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DictCMU',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entry', models.CharField(max_length=255, null=True, blank=True)),
                ('phonemes', models.CharField(max_length=255, null=True, blank=True)),
                ('length', models.IntegerField(null=True, blank=True)),
            ],
        ),
    ]
