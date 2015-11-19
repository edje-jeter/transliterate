#!/usr/bin/env python

import csv
import sys
import os
import urllib2

sys.path.append('..')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

from main.models import DictCMU

# This script will take dictionary entries stored in a local database, pull out
# the arpabet renderings of each entry, remove the "emphasis" codes (ie, the
# numbers 0, 1, and 2), convert the arpabet to unicode deseret, and store
# the deseret in the database. Thus, when the entry gets called, it can return
# the deseret directly without having to do any additional processing.

# Below is the correlation between the Arpabet and the Deseret script.
# Note: This is a provisional correlation for early proof-of-concept
# work; it has serious flaws.
arpa_corr_U = {'IY': u'\uD801\uDC00', 'EY': u'\uD801\uDC01', 'AA': u'\uD801\uDC02', 'AO': u'\uD801\uDC03', 'OW': u'\uD801\uDC04', 'UW': u'\uD801\uDC05', 'IH': u'\uD801\uDC06', 'EH': u'\uD801\uDC07', 'AE': u'\uD801\uDC08', 'AH': u'\uD801\uDC0A', 'UH': u'\uD801\uDC0B', 'AY': u'\uD801\uDC0C', 'AW': u'\uD801\uDC0D', 'W': u'\uD801\uDC0E', 'Y': u'\uD801\uDC0F', 'HH': u'\uD801\uDC10', 'P': u'\uD801\uDC11', 'B': u'\uD801\uDC12', 'T': u'\uD801\uDC13', 'D': u'\uD801\uDC14', 'CH': u'\uD801\uDC15', 'JH': u'\uD801\uDC16', 'K': u'\uD801\uDC17', 'G': u'\uD801\uDC18', 'F': u'\uD801\uDC19', 'V': u'\uD801\uDC1A', 'TH': u'\uD801\uDC1B', 'DH': u'\uD801\uDC1C', 'S': u'\uD801\uDC1D', 'Z': u'\uD801\uDC1E', 'SH': u'\uD801\uDC1F', 'ZH': u'\uD801\uDC20', 'R': u'\uD801\uDC21', 'L': u'\uD801\uDC22', 'M': u'\uD801\uDC23', 'N': u'\uD801\uDC24', 'NG': u'\uD801\uDC25', 'OY': u'\uD801\uDC26', 'ER': u'\uD801\uDC21'}
arpa_corr_m = {'IY': u'\uD801\uDC28', 'EY': u'\uD801\uDC29', 'AA': u'\uD801\uDC2A', 'AO': u'\uD801\uDC2B', 'OW': u'\uD801\uDC2C', 'UW': u'\uD801\uDC2D', 'IH': u'\uD801\uDC2E', 'EH': u'\uD801\uDC2F', 'AE': u'\uD801\uDC30', 'AH': u'\uD801\uDC32', 'UH': u'\uD801\uDC33', 'AY': u'\uD801\uDC34', 'AW': u'\uD801\uDC35', 'W': u'\uD801\uDC36', 'Y': u'\uD801\uDC37', 'HH': u'\uD801\uDC38', 'P': u'\uD801\uDC39', 'B': u'\uD801\uDC3A', 'T': u'\uD801\uDC3B', 'D': u'\uD801\uDC3C', 'CH': u'\uD801\uDC3D', 'JH': u'\uD801\uDC3E', 'K': u'\uD801\uDC3F', 'G': u'\uD801\uDC40', 'F': u'\uD801\uDC41', 'V': u'\uD801\uDC42', 'TH': u'\uD801\uDC43', 'DH': u'\uD801\uDC44', 'S': u'\uD801\uDC45', 'Z': u'\uD801\uDC46', 'SH': u'\uD801\uDC47', 'ZH': u'\uD801\uDC48', 'R': u'\uD801\uDC49', 'L': u'\uD801\uDC4A', 'M': u'\uD801\uDC4B', 'N': u'\uD801\uDC4C', 'NG': u'\uD801\uDC4D', 'OY': u'\uD801\uDC4E', 'ER': u'\uD801\uDC49'}

entries = DictCMU.objects.all()

for entry in entries:

    # ph_list = str(entry.phonemes)
    # entry.phonemes_no_num = ph_list.translate(None, '012')

    # entry.save()
    # print entry.phonemes_no_num

    ph_list = entry.phonemes.split(' ')
    

#     if '(' in line:
#         open_paren = line.index('(')
#         new_entry.variant = int(line[open_paren+1])
#         new_entry.char_length = len(entryword) - 3
#     else:
#         new_entry.variant = 0
#         new_entry.char_length = len(entryword)

#     new_entry.list_length = phonemelist.count(' ') + 1

#     new_entry.save()
# except Exception, e:
#     print e
