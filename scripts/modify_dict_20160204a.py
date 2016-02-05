#!/usr/bin/env python

import sys
import os

sys.path.append('..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

from main.models import DictCMU

dictionary = DictCMU.objects.all()

# for entry in dictionary[0:100]:
for entry in dictionary:
    if '(' in entry.entry:
        stem = entry.entry[0:entry.entry.find('(')]
        print stem
        print entry.entry
    # print '--------------------------- '
    # print entry.entry

    # print entry.phonemes
    # print entry.phonemes_no_num

    # print entry.num_of_variants
    # print entry.variant_num

    # print entry.char_length
    # print entry.list_length

    # if entry.source:
    #     print entry.source
    # else:
    #     entry.source = '0'
    #     print entry.source
