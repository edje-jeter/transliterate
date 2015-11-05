#!/usr/bin/env python

import csv
import sys
import os
import urllib2

sys.path.append('..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

from main.models import DictCMU

# dir_name = os.path.dirname(os.path.abspath(__file__))
# file_name = "cmudict-07b-20151026b.txt"
# cmu_dict_txt = "file://%s" % os.path.join(dir_name, file_name)
# downloaded_data = urllib2.urlopen(cmu_dict_txt)

downloaded_data = urllib2.urlopen('http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b')

# DictCMU.objects.all().delete()

for line in downloaded_data.readlines():
    if ord(line[0]) > 90 or ord(line[0]) < 65:
        continue

    doublespace = line.index('  ')
    entryword = line[:doublespace]

    try:
        new_entry, created = DictCMU.objects.get_or_create(entry=entryword)
        print entryword

        phonemelist = line[doublespace+2:]
        new_entry.phonemes = phonemelist
        print phonemelist

        if '(' in line:
            open_paren = line.index('(')
            new_entry.variant = int(line[open_paren+1])
            new_entry.char_length = len(entryword) - 3
        else:
            new_entry.variant = 0
            new_entry.char_length = len(entryword)

        new_entry.list_length = phonemelist.count(' ') + 1

        new_entry.save()
    except Exception, e:
        print e
