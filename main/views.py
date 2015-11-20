import datetime
import json
import re
import timeit

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext

from main.models import DictCMU


# Get Arpabet correlations for input string; output as list
def match_english_to_arpa(word):
    try:
        arpa_output = DictCMU.objects.get(entry__iexact=word)
        arpa_ph = str(arpa_output.phonemes_no_num).split()
    except Exception, e:
        arpa_ph = ["NO MATCH"]

    return arpa_ph


# Match Arpabet phonemes to unicode Deseret characters
def match_arpa_to_deseret(arpa_ph, word, word_len):
    # Provisional correlation between the Arpabet and the Deseret script.
    # Note: This is for early proof-of-concept; it has serious flaws.
    arpa_corr_U = {'IY': u'\uD801\uDC00', 'EY': u'\uD801\uDC01', 'AA': u'\uD801\uDC02', 'AO': u'\uD801\uDC03', 'OW': u'\uD801\uDC04', 'UW': u'\uD801\uDC05', 'IH': u'\uD801\uDC06', 'EH': u'\uD801\uDC07', 'AE': u'\uD801\uDC08', 'AH': u'\uD801\uDC0A', 'UH': u'\uD801\uDC0B', 'AY': u'\uD801\uDC0C', 'AW': u'\uD801\uDC0D', 'W': u'\uD801\uDC0E', 'Y': u'\uD801\uDC0F', 'HH': u'\uD801\uDC10', 'P': u'\uD801\uDC11', 'B': u'\uD801\uDC12', 'T': u'\uD801\uDC13', 'D': u'\uD801\uDC14', 'CH': u'\uD801\uDC15', 'JH': u'\uD801\uDC16', 'K': u'\uD801\uDC17', 'G': u'\uD801\uDC18', 'F': u'\uD801\uDC19', 'V': u'\uD801\uDC1A', 'TH': u'\uD801\uDC1B', 'DH': u'\uD801\uDC1C', 'S': u'\uD801\uDC1D', 'Z': u'\uD801\uDC1E', 'SH': u'\uD801\uDC1F', 'ZH': u'\uD801\uDC20', 'R': u'\uD801\uDC21', 'L': u'\uD801\uDC22', 'M': u'\uD801\uDC23', 'N': u'\uD801\uDC24', 'NG': u'\uD801\uDC25', 'OY': u'\uD801\uDC26', 'ER': u'\uD801\uDC21'}
    arpa_corr_m = {'IY': u'\uD801\uDC28', 'EY': u'\uD801\uDC29', 'AA': u'\uD801\uDC2A', 'AO': u'\uD801\uDC2B', 'OW': u'\uD801\uDC2C', 'UW': u'\uD801\uDC2D', 'IH': u'\uD801\uDC2E', 'EH': u'\uD801\uDC2F', 'AE': u'\uD801\uDC30', 'AH': u'\uD801\uDC32', 'UH': u'\uD801\uDC33', 'AY': u'\uD801\uDC34', 'AW': u'\uD801\uDC35', 'W': u'\uD801\uDC36', 'Y': u'\uD801\uDC37', 'HH': u'\uD801\uDC38', 'P': u'\uD801\uDC39', 'B': u'\uD801\uDC3A', 'T': u'\uD801\uDC3B', 'D': u'\uD801\uDC3C', 'CH': u'\uD801\uDC3D', 'JH': u'\uD801\uDC3E', 'K': u'\uD801\uDC3F', 'G': u'\uD801\uDC40', 'F': u'\uD801\uDC41', 'V': u'\uD801\uDC42', 'TH': u'\uD801\uDC43', 'DH': u'\uD801\uDC44', 'S': u'\uD801\uDC45', 'Z': u'\uD801\uDC46', 'SH': u'\uD801\uDC47', 'ZH': u'\uD801\uDC48', 'R': u'\uD801\uDC49', 'L': u'\uD801\uDC4A', 'M': u'\uD801\uDC4B', 'N': u'\uD801\uDC4C', 'NG': u'\uD801\uDC4D', 'OY': u'\uD801\uDC4E', 'ER': u'\uD801\uDC49'}

    unic_out = []

    # Not in dictionary
    if arpa_ph == ["NO MATCH"]:
        a = "."*word_len
        unic_out.append(a)

    # No-Caps
    elif word[0].islower():
        for phone in arpa_ph:
            unic_out.append(arpa_corr_m[phone])

    else:
        # Initial-Caps
        if (word_len > 1 and
            (word[1].islower() or
            (word[1] == "'" and word[2].islower())
             )
            ):
                unic_out.append(arpa_corr_U[arpa_ph[0]])
                for i in range(1, len(arpa_ph)):
                    unic_out.append(arpa_corr_m[arpa_ph[i]])

        # All-Caps
        else:
            for phone in arpa_ph:
                unic_out.append(arpa_corr_U[phone])

    return unic_out


# Turn input_str into a list of words
def turn_string_into_list_of_words(input_str):
    rgx = re.compile("(\w[\w']*\w|\w)")
    wlist = rgx.findall(input_str)

    return wlist


# Combine words with characters/spaces
def combine_words_punc_and_spaces(input_len, input_str, wunic):
    temp = []
    wcount = 0
    wflag = True

    for i in range(0, input_len):
        char = input_str[i]

        # find words; use the wflag to signal the end of a word
        if char.isalpha():
            if wflag:
                temp.append(wunic[wcount])
                wflag = False
                wcount += 1
            else:
                pass

        # deal with apostrophes
        elif char == "'":
            if i == 0 or i == input_len:
                temp.append(char)
            if input_str[i-1].isalpha() and input_str[i+1].isalpha():
                pass

        # everything else is non-word and is included
        else:
            temp.append(char)
            wflag = True

    return ''.join(temp)

# -------------------------------------------------------------------


def input_output(request):

    context = {}

    return render_to_response('input_output.html', context,
                              context_instance=RequestContext(request))


# ---- continuous_process: Takes in one word at a time; outputs Deseret ---
def continuous_process(request):

    input_str = request.GET.get('input', '')
    input_len = len(input_str)

    arpa_ph = match_english_to_arpa(input_str)
    unic_out = match_arpa_to_deseret(arpa_ph, input_str, input_len)

    return JsonResponse(unic_out, safe=False)


# ---- batch_process: Takes in whole input at a time; outputs Deseret -----
def batch_process(request):

    input_str = request.GET.get('input', '')
    input_len = len(input_str)
    wlist = turn_string_into_list_of_words(input_str)

    wunic = []
    for w in wlist:
        warpa = match_english_to_arpa(w)
        wlen = len(w)
        temp_str = ''.join(match_arpa_to_deseret(warpa, w, wlen))
        wunic.append(temp_str)

    wunic_str = combine_words_punc_and_spaces(input_len, input_str, wunic)

    return JsonResponse(wunic_str, safe=False)
