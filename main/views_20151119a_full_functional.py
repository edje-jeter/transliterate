import json
import timeit
import datetime
import re

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext

from main.models import DictCMU

from main.forms import EnglishInputForm

# Provisional correlation between the Arpabet and the Deseret script.
# Note: This is for early proof-of-concept; it has serious flaws.
arpa_corr_U = {'IY': u'\uD801\uDC00', 'EY': u'\uD801\uDC01', 'AA': u'\uD801\uDC02', 'AO': u'\uD801\uDC03', 'OW': u'\uD801\uDC04', 'UW': u'\uD801\uDC05', 'IH': u'\uD801\uDC06', 'EH': u'\uD801\uDC07', 'AE': u'\uD801\uDC08', 'AH': u'\uD801\uDC0A', 'UH': u'\uD801\uDC0B', 'AY': u'\uD801\uDC0C', 'AW': u'\uD801\uDC0D', 'W': u'\uD801\uDC0E', 'Y': u'\uD801\uDC0F', 'HH': u'\uD801\uDC10', 'P': u'\uD801\uDC11', 'B': u'\uD801\uDC12', 'T': u'\uD801\uDC13', 'D': u'\uD801\uDC14', 'CH': u'\uD801\uDC15', 'JH': u'\uD801\uDC16', 'K': u'\uD801\uDC17', 'G': u'\uD801\uDC18', 'F': u'\uD801\uDC19', 'V': u'\uD801\uDC1A', 'TH': u'\uD801\uDC1B', 'DH': u'\uD801\uDC1C', 'S': u'\uD801\uDC1D', 'Z': u'\uD801\uDC1E', 'SH': u'\uD801\uDC1F', 'ZH': u'\uD801\uDC20', 'R': u'\uD801\uDC21', 'L': u'\uD801\uDC22', 'M': u'\uD801\uDC23', 'N': u'\uD801\uDC24', 'NG': u'\uD801\uDC25', 'OY': u'\uD801\uDC26', 'ER': u'\uD801\uDC21'}
arpa_corr_m = {'IY': u'\uD801\uDC28', 'EY': u'\uD801\uDC29', 'AA': u'\uD801\uDC2A', 'AO': u'\uD801\uDC2B', 'OW': u'\uD801\uDC2C', 'UW': u'\uD801\uDC2D', 'IH': u'\uD801\uDC2E', 'EH': u'\uD801\uDC2F', 'AE': u'\uD801\uDC30', 'AH': u'\uD801\uDC32', 'UH': u'\uD801\uDC33', 'AY': u'\uD801\uDC34', 'AW': u'\uD801\uDC35', 'W': u'\uD801\uDC36', 'Y': u'\uD801\uDC37', 'HH': u'\uD801\uDC38', 'P': u'\uD801\uDC39', 'B': u'\uD801\uDC3A', 'T': u'\uD801\uDC3B', 'D': u'\uD801\uDC3C', 'CH': u'\uD801\uDC3D', 'JH': u'\uD801\uDC3E', 'K': u'\uD801\uDC3F', 'G': u'\uD801\uDC40', 'F': u'\uD801\uDC41', 'V': u'\uD801\uDC42', 'TH': u'\uD801\uDC43', 'DH': u'\uD801\uDC44', 'S': u'\uD801\uDC45', 'Z': u'\uD801\uDC46', 'SH': u'\uD801\uDC47', 'ZH': u'\uD801\uDC48', 'R': u'\uD801\uDC49', 'L': u'\uD801\uDC4A', 'M': u'\uD801\uDC4B', 'N': u'\uD801\uDC4C', 'NG': u'\uD801\uDC4D', 'OY': u'\uD801\uDC4E', 'ER': u'\uD801\uDC49'}


def input_output(request):

    context = {}

    return render_to_response('input_output.html', context,
                              context_instance=RequestContext(request))


# ---- short_text: takes in one word at a time; outputs Deseret -----
def short_text(request):

    # read data from input box
    input_string = request.GET.get('input', '')
    input_length = len(input_string)

    # Get Arpabet correlations for input string; output as list
    try:
        arpa_output = DictCMU.objects.get(entry__iexact=input_string)
        arpa_ph = str(arpa_output.phonemes_no_num).split()
    except Exception, e:
        arpa_ph = "NO MATCH"

    # Match Arpabet phonemes to unicode Deseret characters
    unic_out = []
    # Not in dictionary
    if arpa_ph == "NO MATCH":
        a = "."*input_length
        unic_out.append(a)

    # No-Caps
    elif input_string[0].islower():
        for phone in arpa_ph:
            unic_out.append(arpa_corr_m[phone])

    else:
        # Initial-Caps
        if (input_length > 1 and
            (input_string[1].islower() or
            (input_string[1] == "'" and input_string[2].islower())
             )
            ):
                unic_out.append(arpa_corr_U[arpa_ph[0]])
                for i in range(1, len(arpa_ph)):
                    unic_out.append(arpa_corr_m[arpa_ph[i]])

        # All-Caps
        else:
            for phone in arpa_ph:
                unic_out.append(arpa_corr_U[phone])

    return JsonResponse(unic_out, safe=False)


def mid_text(request):

    def arpa_corr(word):
        # Given a word, return a list containing the ARPA correlates
        warpa_ph = []
        try:
            arpa_output = DictCMU.objects.get(entry__iexact=word)
            warpa_ph = str(arpa_output.phonemes_no_num).split()
        except Exception, e:
            warpa_ph = ["NO MATCH"]

        return warpa_ph
    # ---------------------------------------------------------------

    context = {}

    input_string = request.GET.get('input', '')
    input_length = len(input_string)

    # Turn input_string into a list of words
    rgx = re.compile("(\w[\w']*\w|\w)")
    wlist = rgx.findall(input_string)
    print "wlist: %s" % wlist

    # Get ARPA correlates and map capitalization in wlist
    wunic = []
    for w in wlist:
        warpa = arpa_corr(w)
        wlen = len(w)
        temp = []

        if warpa == ["NO MATCH"]:
            a = "." * wlen
            temp.append(a)
        else:
            if w[0].islower():
                #  No-Caps
                for phone in warpa:
                    temp.append(arpa_corr_m[phone])
            else:
                if wlen > 1 and (w[1].islower() or (w[1] == "'" and w[2].islower())):
                    # Initial-Caps
                    temp.append(arpa_corr_U[warpa[0]])
                    for i in range(1, len(warpa)):
                        temp.append(arpa_corr_m[warpa[i]])
                else:
                    # All-Caps
                    for phone in warpa:
                        temp.append(arpa_corr_U[phone])

        wunic.append(''.join(temp))

    # Combine words with characters/spaces
    b = []
    wcount = 0
    wflag = True

    for i in range(0, input_length):
        char = input_string[i]

        # find words; use the wflag to signal the end of a word
        if char.isalpha():
            if wflag:
                b.append(wunic[wcount])
                wflag = False
                wcount += 1
            else:
                pass

        # deal with apostrophes
        elif char == "'":
            if i == 0 or i == input_length:
                b.append(char)
            if input_string[i-1].isalpha() and input_string[i+1].isalpha():
                pass

        # everything else is non-word and is included
        else:
            b.append(char)
            wflag = True

    wunic_str = ''.join(b)

    return JsonResponse(wunic_str, safe=False)
