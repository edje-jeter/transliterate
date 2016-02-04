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
        # a = "_"*word_len
        a = "<span id='fault-" + word + "'" + " class='fault-underscore'>" + "_"*word_len + "</span>"
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


def match_arpa_positional(warpa, dictionary):
    dict_i = dictionary['i']
    dict_m = dictionary['m']
    dict_t = dictionary['t']

    unic_out = []

    warpa_len = len(warpa)

    # # Standalone character
    # if warpa_len = 2

    # Initial character
    unic_out.append(dict_i[warpa[0]])

    # Medial character(s)
    for i in range(1, warpa_len - 1):
        unic_out.append(dict_m[warpa[i]])

    # Terminal character
    unic_out.append(dict_t[warpa[warpa_len - 1]])
    print unic_out

    return unic_out


# ---- batch_process: Takes in whole input at a time; outputs Deseret -----
def batch_process(request):

    input_str = request.GET.get('input', '')
    input_len = len(input_str)
    wlist = turn_string_into_list_of_words(input_str)

    wunic = []
    fault_list = []
    for w in wlist:
        warpa = match_english_to_arpa(w)
        if warpa == ["NO MATCH"]:
            fault_list.append(w)
        wlen = len(w)
        temp_str = ''.join(match_arpa_to_deseret(warpa, w, wlen))
        wunic.append(temp_str)

    wunic_str = combine_words_punc_and_spaces(input_len, input_str, wunic)
    print fault_list

    output = [wunic_str, fault_list]

    return JsonResponse(output, safe=False)


# ---- correlate_arpa_to_unicode: given Arpa phones, returns unicode
def correlate_arpa_to_unicode(warpa):
    print 'made it to catu'
    # Provisional correlation between the Arpabet and scripts.
    # This is for proof-of-concept; it has serious flaws.
    # U = upper case; l = lower case; i = initial; m = medial;
    # t = terminal; s = stand-alone

    # Non-positional, non-case
    arpa_respell = {'B': 'b', 'G': 'g', 'JH': 'j', 'D': 'd', 'HH': 'h', 'V': 'v', 'Z': 'z', 'ZH': 'zh', 'Y': 'y', 'K': 'k', 'L': 'l', 'M': 'm', 'N': 'n', 'S': 's', 'F': 'f', 'P': 'p', 'CH': 'ch', 'R': 'r', 'SH': 'sh', 'T': 't', 'AY': 'ai', 'AW': 'ao', 'EY': 'ei', 'OW': 'o', 'OY': 'oi', 'DH': 'dh', 'TH': 'th', 'AE': 'a', 'AA': 'ah', 'AX': '\u018F', 'EH': 'eh', 'IY': 'ee', 'IH': 'i', 'AO': 'aw', 'UW': 'ew', 'UH': 'uu', 'AH': 'uh', 'NG': 'ng', 'ER': 'er', 'W': 'w'}
    arpa_ipa = {'B': u'\u0062', 'G': u'\u0261', 'JH': u'\u02A4', 'D': u'\u0064', 'HH': u'\u0068', 'V': u'\u0076', 'Z': u'\u007A', 'ZH': u'\u0292', 'Y': u'\u006A', 'K': u'\u006B', 'L': u'\u026B', 'M': u'\u006D', 'N': u'\u006E', 'S': u'\u0073', 'F': u'\u0066', 'P': u'\u0070', 'CH': u'\u02A7', 'R': u'\u0072', 'SH': u'\u0283', 'T': u'\u0074', 'AY': u'\u0061\u026A', 'AW': u'\u0061\u028A', 'EY': u'\u025B\u026A', 'OW': u'\u006F\u028A', 'OY': u'\u0254\u026A', 'DH': u'\u00F0', 'TH': u'\u03B8', 'AE': u'\u00E6', 'AA': u'\u0251', 'AX': u'\u0259', 'EH': u'\u025B', 'IY': u'\u0069', 'IH': u'\u026A', 'AO': u'\u0254', 'UW': u'\u0075', 'UH': u'\u028A', 'AH': u'\u028C', 'NG': u'\u014B', 'ER': u'\u025D', 'W': u'\u0077'}
    arpa_greek_U = {'AA': u'\u0391', 'AE': u'\u0391', 'AH': u'\u039F\u03A5', 'AO': u'\u039F', 'AW': u'\u0391\u03A5', 'AX': u'\u0391', 'AY': u'\u0391\u0399', 'B': u'\u0392', 'CH': u'\u03A7', 'D': u'\u0394', 'DH': u'\u0398', 'EH': u'\u0395', 'ER': u'\u0395\u03A1', 'EY': u'\u0397', 'F': u'\u03A6', 'G': u'\u0393', 'HH': u'\u1FFE', 'IH': u'\u0399', 'IY': u'\u0399', 'JH': u'\u0393', 'K': u'\u039A', 'L': u'\u039B', 'M': u'\u039C', 'N': u'\u039D', 'NG': u'\u039D\u0393', 'OW': u'\u03A9', 'OY': u'\u039F\u0399', 'P': u'\u03A0', 'R': u'\u03A1', 'S': u'\u03A3', 'SH': u'\u03A3', 'T': u'\u03A4', 'TH': u'\u0398', 'UH': u'\u039F\u03A5', 'UW': u'\u039F\u03A5', 'V': u'\u0392', 'W': u'\u03A5', 'Y': u'\u0399', 'Z': u'\u0396', 'ZH': u'\u0396'}

    # Case-based (ie, mixes upper and lower cases), non-positional
    arpa_deseret_U = {'IY': u'\uD801\uDC00', 'EY': u'\uD801\uDC01', 'AA': u'\uD801\uDC02', 'AO': u'\uD801\uDC03', 'OW': u'\uD801\uDC04', 'UW': u'\uD801\uDC05', 'IH': u'\uD801\uDC06', 'EH': u'\uD801\uDC07', 'AE': u'\uD801\uDC08', 'AH': u'\uD801\uDC0A', 'AX': u'\uD801\uDC0A', 'UH': u'\uD801\uDC0B', 'AY': u'\uD801\uDC0C', 'AW': u'\uD801\uDC0D', 'W': u'\uD801\uDC0E', 'Y': u'\uD801\uDC0F', 'HH': u'\uD801\uDC10', 'P': u'\uD801\uDC11', 'B': u'\uD801\uDC12', 'T': u'\uD801\uDC13', 'D': u'\uD801\uDC14', 'CH': u'\uD801\uDC15', 'JH': u'\uD801\uDC16', 'K': u'\uD801\uDC17', 'G': u'\uD801\uDC18', 'F': u'\uD801\uDC19', 'V': u'\uD801\uDC1A', 'TH': u'\uD801\uDC1B', 'DH': u'\uD801\uDC1C', 'S': u'\uD801\uDC1D', 'Z': u'\uD801\uDC1E', 'SH': u'\uD801\uDC1F', 'ZH': u'\uD801\uDC20', 'R': u'\uD801\uDC21', 'L': u'\uD801\uDC22', 'M': u'\uD801\uDC23', 'N': u'\uD801\uDC24', 'NG': u'\uD801\uDC25', 'OY': u'\uD801\uDC26', 'ER': u'\uD801\uDC21'}
    arpa_deseret_L = {'IY': u'\uD801\uDC28', 'EY': u'\uD801\uDC29', 'AA': u'\uD801\uDC2A', 'AO': u'\uD801\uDC2B', 'OW': u'\uD801\uDC2C', 'UW': u'\uD801\uDC2D', 'IH': u'\uD801\uDC2E', 'EH': u'\uD801\uDC2F', 'AE': u'\uD801\uDC30', 'AH': u'\uD801\uDC32', 'AX': u'\uD801\uDC32', 'UH': u'\uD801\uDC33', 'AY': u'\uD801\uDC34', 'AW': u'\uD801\uDC35', 'W': u'\uD801\uDC36', 'Y': u'\uD801\uDC37', 'HH': u'\uD801\uDC38', 'P': u'\uD801\uDC39', 'B': u'\uD801\uDC3A', 'T': u'\uD801\uDC3B', 'D': u'\uD801\uDC3C', 'CH': u'\uD801\uDC3D', 'JH': u'\uD801\uDC3E', 'K': u'\uD801\uDC3F', 'G': u'\uD801\uDC40', 'F': u'\uD801\uDC41', 'V': u'\uD801\uDC42', 'TH': u'\uD801\uDC43', 'DH': u'\uD801\uDC44', 'S': u'\uD801\uDC45', 'Z': u'\uD801\uDC46', 'SH': u'\uD801\uDC47', 'ZH': u'\uD801\uDC48', 'R': u'\uD801\uDC49', 'L': u'\uD801\uDC4A', 'M': u'\uD801\uDC4B', 'N': u'\uD801\uDC4C', 'NG': u'\uD801\uDC4D', 'OY': u'\uD801\uDC4E', 'ER': u'\uD801\uDC49'}

    # Positional (ie, characters change depending on where in word they appear)
    arpa_greek_l_i = {'AA': u'\u03B1', 'AE': u'\u03B1', 'AH': u'\u03BF\u03C5', 'AO': u'\u03BF', 'AW': u'\u03B1\u03B9', 'AX': u'\u03B1', 'AY': u'\u03B1\u03B9', 'B': u'\u03B2', 'CH': u'\u03C7', 'D': u'\u03B4', 'DH': u'\u03B8', 'EH': u'\u03B5', 'ER': u'\u03B5\u03C1', 'EY': u'\u03B7', 'F': u'\u03C6', 'G': u'\u03B3', 'HH': u'\u1FFE', 'IH': u'\u03B9', 'IY': u'\u03B9', 'JH': u'\u03B3', 'K': u'\u03BA', 'L': u'\u03BB', 'M': u'\u03BC', 'N': u'\u03BD', 'NG': u'\u03BD\u03B3', 'OW': u'\u03C9', 'OY': u'\u03BF\u03B9', 'P': u'\u03C0', 'R': u'\u03C1', 'S': u'\u03C3', 'SH': u'\u03C3', 'T': u'\u03C4', 'TH': u'\u03B8', 'UH': u'\u03BF\u03C5', 'UW': u'\u03BF\u03C5', 'V': u'\u03B2', 'W': u'\u03C5', 'Y': u'\u03B9', 'Z': u'\u03B6', 'ZH': u'\u03B6'}
    arpa_greek_l_t = {'AA': u'\u03B1', 'AE': u'\u03B1', 'AH': u'\u03BF\u03C5', 'AO': u'\u03BF', 'AW': u'\u03B1\u03B9', 'AX': u'\u03B1', 'AY': u'\u03B1\u03B9', 'B': u'\u03B2', 'CH': u'\u03C7', 'D': u'\u03B4', 'DH': u'\u03B8', 'EH': u'\u03B5', 'ER': u'\u03B5\u03C1', 'EY': u'\u03B7', 'F': u'\u03C6', 'G': u'\u03B3', 'HH': u'\u1FFE', 'IH': u'\u03B9', 'IY': u'\u03B9', 'JH': u'\u03B3', 'K': u'\u03BA', 'L': u'\u03BB', 'M': u'\u03BC', 'N': u'\u03BD', 'NG': u'\u03BD\u03B3', 'OW': u'\u03C9', 'OY': u'\u03BF\u03B9', 'P': u'\u03C0', 'R': u'\u03C1', 'S': u'\u03C2', 'SH': u'\u03C2', 'T': u'\u03C4', 'TH': u'\u03B8', 'UH': u'\u03BF\u03C5', 'UW': u'\u03BF\u03C5', 'V': u'\u03B2', 'W': u'\u03C5', 'Y': u'\u03B9', 'Z': u'\u03B6', 'ZH': u'\u03B6'}

    arpa_hebrew_i = {'AA': u'', 'AE': u'', 'AH': u'\u05D5', 'AO': u'', 'AW': u'\u05D0\u05D5', 'AX': u'', 'AY': u'\u05F0', 'B': u'\u05D1', 'CH': u'\u05E6\u05F3', 'D': u'\u05D3', 'DH': u'\u05D3', 'EH': u'', 'ER': u'\u05E8', 'EY': u'\u05F0', 'F': u'\u05E4', 'G': u'\u05D2', 'HH': u'\u05D4', 'IH': u'', 'IY': u'\u05D9', 'JH': u'\u05D2\u05F3', 'K': u'\u05DB', 'L': u'\u05DC', 'M': u'\u05DE', 'N': u'\u05E0', 'NG': u'\u05E0\u05D2', 'OW': u'\u05D5', 'OY': u'\u05F1', 'P': u'\uFB44', 'R': u'\u05E8', 'S': u'\u05E1', 'SH': u'\u05E9', 'T': u'\u05D8', 'TH': u'\u05EA', 'UH': u'\u05D5', 'UW': u'\u05D5', 'V': u'\u05D5', 'W': u'\u05D5', 'Y': u'\u05D9', 'Z': u'\u05D6', 'ZH': u'\u05D6\u05F3'}
    arpa_hebrew_t = {'AA': u'', 'AE': u'', 'AH': u'\u05D5', 'AO': u'', 'AW': u'\u05D0\u05D5', 'AX': u'', 'AY': u'\u05F0', 'B': u'\u05D1', 'CH': u'\u05E5\u05F3', 'D': u'\u05D3', 'DH': u'\u05D3', 'EH': u'', 'ER': u'\u05E8', 'EY': u'\u05F0', 'F': u'\u05E3', 'G': u'\u05D2', 'HH': u'\u05D4', 'IH': u'', 'IY': u'\u05D9', 'JH': u'\u05D2\u05F3', 'K': u'\u05DA', 'L': u'\u05DC', 'M': u'\u05DD', 'N': u'\u05DF', 'NG': u'\u05E0\u05D2', 'OW': u'\u05D5', 'OY': u'\u05F1', 'P': u'\uFB43', 'R': u'\u05E8', 'S': u'\u05E1', 'SH': u'\u05E9', 'T': u'\u05D8', 'TH': u'\u05EA', 'UH': u'\u05D5', 'UW': u'\u05D5', 'V': u'\u05D5', 'W': u'\u05D5', 'Y': u'\u05D9', 'Z': u'\u05D6', 'ZH': u'\u05D6\u05F3'}

    arpa_arabic_s = {'AA': u'\uFE83', 'AE': u'', 'AH': u'', 'AO': u'\uFE83', 'AW': u'', 'AX': u'', 'AY': u'\uFECB\uFECB', 'B': u'\uFE8F', 'CH': u'\uFE9D', 'D': u'\uFEA9', 'DH': u'\uFEAB', 'EH': u'\uFE83', 'ER': u'\uFEAD', 'EY': u'\uFEF1', 'F': u'\uFED1', 'G': u'\uFECD', 'HH': u'\uFEE9', 'IH': u'', 'IY': u'\uFEF1', 'JH': u'\uFE9D', 'K': u'\uFED9', 'L': u'\uFEDD', 'M': u'\uFEE1', 'N': u'\uFEE5', 'NG': u'\uFEE7\uFECE', 'OW': u'', 'OY': u'', 'P': u'\uFE8F', 'R': u'\uFEAD', 'S': u'\uFEB1', 'SH': u'\uFEB5', 'T': u'\uFE95', 'TH': u'\uFE99', 'UH': u'\uFEED', 'UW': u'\uFEED', 'V': u'\uFED1', 'W': u'\uFEED', 'Y': u'\uFEF1', 'Z': u'\uFEAF', 'ZH': u'\uFEB5'}
    arpa_arabic_i = {'AA': u'\uFE83', 'AE': u'', 'AH': u'', 'AO': u'\uFE83', 'AW': u'', 'AX': u'', 'AY': u'\uFECB\uFEF4', 'B': u'\uFE91', 'CH': u'\uFE9F', 'D': u'\uFEA9', 'DH': u'\uFEAB', 'EH': u'\uFE83', 'ER': u'\uFEAD', 'EY': u'\uFEF3', 'F': u'\uFED3', 'G': u'\uFECF', 'HH': u'\uFEEB', 'IH': u'', 'IY': u'\uFEF3', 'JH': u'\uFE9F', 'K': u'\uFEDB', 'L': u'\uFEDF', 'M': u'\uFEE3', 'N': u'\uFEE7', 'NG': u'\uFEE7\uFED0', 'OW': u'', 'OY': u'', 'P': u'\uFE91', 'R': u'\uFEAD', 'S': u'\uFEB3', 'SH': u'\uFEB7', 'T': u'\uFE97', 'TH': u'\uFE9B', 'UH': u'\uFEED', 'UW': u'\uFEED', 'V': u'\uFED3', 'W': u'\uFEED', 'Y': u'\uFEF3', 'Z': u'\uFEAF', 'ZH': u'\uFEB7'}
    arpa_arabic_m = {'AA': u'\uFE84', 'AE': u'', 'AH': u'', 'AO': u'\uFE84', 'AW': u'', 'AX': u'', 'AY': u'\uFECC\uFEF4', 'B': u'\uFE92', 'CH': u'\uFEA0', 'D': u'\uFEAA', 'DH': u'\uFEAC', 'EH': u'\uFE84', 'ER': u'\uFEAE', 'EY': u'\uFEF4', 'F': u'\uFED4', 'G': u'\uFED0', 'HH': u'\uFEEC', 'IH': u'', 'IY': u'\uFEF4', 'JH': u'\uFEA0', 'K': u'\uFEDC', 'L': u'\uFEE0', 'M': u'\uFEE4', 'N': u'\uFEE8', 'NG': u'\uFEE8\uFED0', 'OW': u'', 'OY': u'', 'P': u'\uFE92', 'R': u'\uFEAE', 'S': u'\uFEB4', 'SH': u'\uFEB8', 'T': u'\uFE98', 'TH': u'\uFE9C', 'UH': u'\uFEEE', 'UW': u'\uFEEE', 'V': u'\uFED4', 'W': u'\uFEEE', 'Y': u'\uFEF4', 'Z': u'\uFEB0', 'ZH': u'\uFEB8'}
    arpa_arabic_t = {'AA': u'\uFE84', 'AE': u'', 'AH': u'', 'AO': u'\uFE84', 'AW': u'', 'AX': u'', 'AY': u'\uFECB\uFEF2', 'B': u'\uFE90', 'CH': u'\uFE9E', 'D': u'\uFEAA', 'DH': u'\uFEAC', 'EH': u'\uFE84', 'ER': u'\uFEAE', 'EY': u'\uFEF2', 'F': u'\uFED2', 'G': u'\uFECE', 'HH': u'\uFEEA', 'IH': u'', 'IY': u'\uFEF2', 'JH': u'\uFE9E', 'K': u'\uFEDA', 'L': u'\uFEDE', 'M': u'\uFEE2', 'N': u'\uFEE6', 'NG': u'\uFEE8\uFECE', 'OW': u'', 'OY': u'', 'P': u'\uFE90', 'R': u'\uFEAE', 'S': u'\uFEB2', 'SH': u'\uFEB6', 'T': u'\uFE96', 'TH': u'\uFE9A', 'UH': u'\uFEEE', 'UW': u'\uFEEE', 'V': u'\uFED2', 'W': u'\uFEEE', 'Y': u'\uFEF2', 'Z': u'\uFEB0', 'ZH': u'\uFEB6'}

    # Dictionary combinations
    dict_greek_l = {'s': arpa_greek_l_i, 'i': arpa_greek_l_i, 'm': arpa_greek_l_i, 't': arpa_greek_l_t}
    dict_hebrew = {'s': arpa_hebrew_i, 'i': arpa_hebrew_i, 'm': arpa_hebrew_i, 't': arpa_hebrew_t}
    dict_arabic = {'s': arpa_arabic_s, 'i': arpa_arabic_i, 'm': arpa_arabic_m, 't': arpa_arabic_t}

    dict_list_np = [arpa_respell,
                    arpa_ipa,
                    arpa_greek_U,
                    ]

    dict_list_p = [dict_greek_l,
                   dict_hebrew,
                   dict_arabic,
                   ]

    print 'made it to right before for loop'
    unic_out = []

    # non-positional scripts (and we're doing Deseret elsewhere)
    for dictionary in dict_list_np:
        temp_list = []
        for w in warpa:
            temp_list.append(dictionary[w])
        temp_str = ''.join(temp_list)
        # print 'temp_str: %s' % temp_str
        unic_out.append(temp_str)
    # print 'unic_out: %s' % unic_out

    # positional scripts
    for dictionary in dict_list_p:
        unic_out.append(''.join(match_arpa_positional(warpa, dictionary)))

    return unic_out


# ---- batch_get_arpa: Takes in whole input; outputs Arpabet -----
def name_batch_process(request):

    input_str = request.GET.get('input', '')
    input_len = len(input_str)
    wlist = turn_string_into_list_of_words(input_str)

    wunic = []
    unic_out = []
    for w in wlist:
        warpa = match_english_to_arpa(w)
        # print 'warpa: %s' % warpa
        if warpa == ["NO MATCH"]:
            # print 'no match trigger'
            unic_out.append(warpa)
        else:
            unic_out.append(' '.join(warpa))
            wlen = len(w)
            temp_str = ''.join(match_arpa_to_deseret(warpa, w, wlen))
            wunic.append(temp_str)
            print 'right before correlate_arpa_to_unicode'
            unic_out_temp = correlate_arpa_to_unicode(warpa)
            print 'right after correlate_arpa_to_unicode'

            for temp in unic_out_temp:
                unic_out.append(temp)

            unic_out.append(combine_words_punc_and_spaces(input_len, input_str, wunic))

    return JsonResponse(unic_out, safe=False)


# ---- arpabet_entry: Provides info to generate buttons to enter pronunciation
def arpabet_entry(request):

    context = {}

# Lists to generate Arpabet entry buttons:
    # [Arpabet symbol, button symbol, example word in three parts]
    # The second part of example (column 3) is highlighted
    # context['arpa_btns'] = [
    #     ['B', 'b', '', 'b', 'uy', 'stop', u'\u0062'],
    #     ['D', 'd', '', 'd', 'ay', 'stop', u'\u0064'],
    #     ['G', 'g', '', 'g', 'o', 'stop', u'\u0261'],
    #     ['K', 'k', '', 'k', 'ey', 'stop', u'\u006B'],
    #     ['P', 'p', '', 'p', 'ay', 'stop', u'\u0070'],
    #     ['T', 't', '', 't', 'ake', 'stop', u'\u0074'],
    #     ['F', 'f', '', 'f', 'or', 'fricative', u'\u0066'],
    #     ['HH', 'h', '', 'h', 'ouse', 'fricative', u'\u0068'],
    #     ['S', 's', '', 's', 'ay', 'fricative', u'\u0073'],
    #     ['SH', 'sh', '', 'sh', 'ow', 'fricative', u'\u0283'],
    #     ['TH', 'th', '', 'th', 'anks', 'fricative', u'\u03B8'],
    #     ['DH', 'dh', '', 'th', 'at', 'fricative', u'\u00F0'],
    #     ['V', 'v', '', 'v', 'ery', 'fricative', u'\u0076'],
    #     ['Z', 'z', '', 'z', 'oo', 'fricative', u'\u007A'],
    #     ['ZH', 'zh', 'A', 's', 'ia', 'fricative', u'\u0292'],
    #     ['CH', 'ch', '', 'ch', 'air', 'affricate', u'\u02A7'],
    #     ['JH', 'j', '', 'j', 'ust', 'affricate', u'\u02A4'],
    #     ['L', 'l', '', 'l', 'ate', 'liquid', u'\u026B'],
    #     ['R', 'r', '', 'r', 'un', 'liquid', u'\u0072'],
    #     ['M', 'm', '', 'm', 'an', 'nasal', u'\u006D'],
    #     ['N', 'n', '', 'n', 'o', 'nasal', u'\u006E'],
    #     ['NG', 'ng', 'si', 'ng', '', 'nasal', u'\u014B'],
    #     ['ER', 'er', 'h', 'er', '', 'r_colored', u'\u025D'],
    #     ['W', 'w', '', 'w', 'ay', 'semi_vowel', u'\u0077'],
    #     ['Y', 'y', '', 'y', 'es', 'semi_vowel', u'\u006A'],
    #     ['AA', 'ah', 'f', 'a', 'ther', 'monophthong', u'\u0251'],
    #     ['AE', 'a', 'f', 'a', 'st', 'monophthong', u'\u00E6'],
    #     ['AH', 'u', 'b', 'u', 't', 'monophthong', u'\u028C'],
    #     ['AO', 'aw', 'f', 'a', 'll', 'monophthong', u'\u0254'],
    #     ['AX', u'\u018F', 'disc', 'u', 's', 'monophthong', u'\u0259'],
    #     ['EH', 'eh', 'r', 'e', 'd', 'monophthong', u'\u025B'],
    #     ['IH', 'i', 'b', 'i', 'g', 'monophthong', u'\u026A'],
    #     ['IY', 'ee', 'b', 'ee', '', 'monophthong', u'\u0069'],
    #     ['UH', 'uu', 'sh', 'ou', 'ld', 'monophthong', u'\u028A'],
    #     ['UW', 'ew', 'y', 'ou', '', 'monophthong', u'\u0075'],
    #     ['AW', 'ao', 'h', 'ow', '', 'diphthong', u'\u0061\u028A'],
    #     ['AY', 'ai', 'm', 'y', '', 'diphthong', u'\u0061\u026A'],
    #     ['EY', 'ei', 's', 'at', '', 'diphthong', u'\u025B\u026A'],
    #     ['OW', 'o', 'sh', 'ow', '', 'diphthong', u'\u006F\u028A'],
    #     ['OY', 'oi', 'b', 'oy', '', 'diphthong', u'\u0254\u026A'],
    # ]

# QWERTY-based layout
    context['qwerty_top'] = [
        ['', '', '', '', '', '', ''],
        ['W', 'w', '', 'w', 'ay', 'semi_vowel', u'\u0077'],
        ['', '', '', '', '', '', ''],
        ['R', 'r', '', 'r', 'un', 'liquid', u'\u0072'],
        ['T', 't', '', 't', 'ake', 'stop', u'\u0074'],
        ['Y', 'y', '', 'y', 'es', 'semi_vowel', u'\u006A'],
        ['', '', '', '', '', '', ''],
        ['', '', '', '', '', '', ''],
        ['', '', '', '', '', '', ''],
        ['P', 'p', '', 'p', 'ay', 'stop', u'\u0070'],
    ]

    context['qwerty_mid'] = [
        ['', '', '', '', '', '', ''],
        ['S', 's', '', 's', 'ay', 'fricative', u'\u0073'],
        ['D', 'd', '', 'd', 'ay', 'stop', u'\u0064'],
        ['F', 'f', '', 'f', 'or', 'fricative', u'\u0066'],
        ['G', 'g', '', 'g', 'o', 'stop', u'\u0261'],
        ['HH', 'h', '', 'h', 'ouse', 'fricative', u'\u0068'],
        ['JH', 'j', '', 'j', 'ust', 'affricate', u'\u02A4'],
        ['K', 'k', '', 'k', 'ey', 'stop', u'\u006B'],
        ['L', 'l', '', 'l', 'ate', 'liquid', u'\u026B'],
    ]

    context['qwerty_bot'] = [
        ['Z', 'z', '', 'z', 'oo', 'fricative', u'\u007A'],
        ['', '', '', '', '', '', ''],
        ['', '', '', '', '', '', ''],
        ['V', 'v', '', 'v', 'ery', 'fricative', u'\u0076'],
        ['B', 'b', '', 'b', 'uy', 'stop', u'\u0062'],
        ['N', 'n', '', 'n', 'o', 'nasal', u'\u006E'],
        ['M', 'm', '', 'm', 'an', 'nasal', u'\u006D'],
    ]

    context['fricative'] = [
        ['SH', 'sh', '', 'sh', 'ow', 'fricative', u'\u0283'],
        ['TH', 'th', '', 'th', 'ank', 'fricative', u'\u03B8'],
        ['DH', 'dh', '', 'th', 'at', 'fricative', u'\u00F0'],
        ['ZH', 'zh', 'A', 's', 'ia', 'fricative', u'\u0292'],
        ['CH', 'ch', '', 'ch', 'air', 'affricate', u'\u02A7'],
    ]

    context['ng_and_er'] = [
        ['NG', 'ng', 'si', 'ng', '', 'nasal', u'\u014B'],
        ['', '', '', '', '', '', ''],
        ['ER', 'er', 'h', 'er', '', 'r_colored', u'\u025D'],
    ]

    context['monophthong1'] = [
        ['AA', 'ah', 'f', 'a', 'ther', 'monophthong', u'\u0251'],
        ['AO', 'aw', 'f', 'a', 'll', 'monophthong', u'\u0254'],
        ['AE', 'a', 'f', 'a', 'st', 'monophthong', u'\u00E6'],
        ['AH', 'uh', 'b', 'u', 't', 'monophthong', u'\u028C'],
        ['AX', u'\u018F', 'disc', 'u', 's', 'monophthong', u'\u0259'],
    ]

    context['monophthong2'] = [
        ['EH', 'eh', 'r', 'e', 'd', 'monophthong', u'\u025B'],
        ['IH', 'i', 'b', 'i', 'g', 'monophthong', u'\u026A'],
        ['IY', 'ee', 'b', 'ee', '', 'monophthong', u'\u0069'],
        ['UH', 'uu', 'c', 'ou', 'ld', 'monophthong', u'\u028A'],
        ['UW', 'ew', 'y', 'ou', '', 'monophthong', u'\u0075'],
    ]

    context['diphthong'] = [
        ['AW', 'ao', 'h', 'ow', '', 'diphthong', u'\u0061\u028A'],
        ['AY', 'ai', 'm', 'y', '', 'diphthong', u'\u0061\u026A'],
        ['EY', 'ei', 's', 'at', '', 'diphthong', u'\u025B\u026A'],
        ['OW', 'o', 'sh', 'ow', '', 'diphthong', u'\u006F\u028A'],
        ['OY', 'oi', 'b', 'oy', '', 'diphthong', u'\u0254\u026A'],
    ]

    return render_to_response('arpabet_entry.html', context,
                              context_instance=RequestContext(request))


# ---- Keyboard generator: makes JSON for AJAX keyboard
def generate_keyboard(request):

    keyboard_list = [
        ['', '', '', '', '', '', '', 'qwerty-top', 'qwerty-btn qwerty-disabled'],
        ['W', 'w', '', 'w', 'ay', 'semi_vowel', u'\u0077', 'qwerty-top', 'keyboard-btn qwerty-btn'],
        ['', '', '', '', '', '', '', 'qwerty-top', 'qwerty-btn qwerty-disabled'],
        ['R', 'r', '', 'r', 'un', 'liquid', u'\u0072', 'qwerty-top', 'keyboard-btn qwerty-btn'],
        ['T', 't', '', 't', 'ake', 'stop', u'\u0074', 'qwerty-top', 'keyboard-btn qwerty-btn'],
        ['Y', 'y', '', 'y', 'es', 'semi_vowel', u'\u006A', 'qwerty-top', 'keyboard-btn qwerty-btn'],
        ['', '', '', '', '', '', '', 'qwerty-top', 'qwerty-btn qwerty-disabled'],
        ['', '', '', '', '', '', '', 'qwerty-top', 'qwerty-btn qwerty-disabled'],
        ['', '', '', '', '', '', '', 'qwerty-top', 'qwerty-btn qwerty-disabled'],
        ['P', 'p', '', 'p', 'ay', 'stop', u'\u0070', 'qwerty-top', 'keyboard-btn qwerty-btn'],
        ['', '', '', '', '', '', '', 'qwerty-mid', 'qwerty-btn qwerty-disabled'],
        ['S', 's', '', 's', 'ay', 'fricative', u'\u0073', 'qwerty-mid', 'keyboard-btn qwerty-btn'],
        ['D', 'd', '', 'd', 'ay', 'stop', u'\u0064', 'qwerty-mid', 'keyboard-btn qwerty-btn'],
        ['F', 'f', '', 'f', 'or', 'fricative', u'\u0066', 'qwerty-mid', 'keyboard-btn qwerty-btn'],
        ['G', 'g', '', 'g', 'o', 'stop', u'\u0261', 'qwerty-mid', 'keyboard-btn qwerty-btn'],
        ['HH', 'h', '', 'h', 'ouse', 'fricative', u'\u0068', 'qwerty-mid', 'keyboard-btn qwerty-btn'],
        ['JH', 'j', '', 'j', 'ust', 'affricate', u'\u02A4', 'qwerty-mid', 'keyboard-btn qwerty-btn'],
        ['K', 'k', '', 'k', 'ey', 'stop', u'\u006B', 'qwerty-mid', 'keyboard-btn qwerty-btn'],
        ['L', 'l', '', 'l', 'ate', 'liquid', u'\u026B', 'qwerty-mid', 'keyboard-btn qwerty-btn'],
        ['Z', 'z', '', 'z', 'oo', 'fricative', u'\u007A', 'qwerty-bot', 'keyboard-btn qwerty-btn'],
        ['', '', '', '', '', '', '', 'qwerty-bot', 'qwerty-btn qwerty-disabled'],
        ['', '', '', '', '', '', '', 'qwerty-bot', 'qwerty-btn qwerty-disabled'],
        ['V', 'v', '', 'v', 'ery', 'fricative', u'\u0076', 'qwerty-bot', 'keyboard-btn qwerty-btn'],
        ['B', 'b', '', 'b', 'uy', 'stop', u'\u0062', 'qwerty-bot', 'keyboard-btn qwerty-btn'],
        ['N', 'n', '', 'n', 'o', 'nasal', u'\u006E', 'qwerty-bot', 'keyboard-btn qwerty-btn'],
        ['M', 'm', '', 'm', 'an', 'nasal', u'\u006D', 'qwerty-bot', 'keyboard-btn qwerty-btn'],
        ['CH', 'ch', '', 'ch', 'at', 'affricate', u'\u02A7', 'combo-fricative', 'keyboard-btn pronunc-btn pronunc-affricate'],
        ['SH', 'sh', '', 'sh', 'e', 'fricative', u'\u0283', 'combo-fricative', 'keyboard-btn pronunc-btn pronunc-fricative'],
        ['ZH', 'zh', 'A', 's', 'ia', 'fricative', u'\u0292', 'combo-fricative', 'keyboard-btn pronunc-btn pronunc-fricative'],
        ['TH', 'th', '', 'th', 'in', 'fricative', u'\u03B8', 'combo-fricative', 'keyboard-btn pronunc-btn pronunc-fricative'],
        ['DH', 'dh', '', 'th', 'e', 'fricative', u'\u00F0', 'combo-fricative', 'keyboard-btn pronunc-btn pronunc-fricative'],
        ['', '', '', '', '', '', '', 'qwerty-space', 'space-spacer-left'],
        ['', 'Space', '', '', '', '', '', 'qwerty-space', 'space-back-row-btn space-bar-btn'],
        ['', '', '', '', '', '', '', 'qwerty-space', 'space-spacer-right'],
        ['', u'\u232B' + ' Back', '', '', '', '', '', 'qwerty-space', 'space-back-row-btn backspace-btn'],
        ['NG', 'ng', 'si', 'ng', '', 'nasal', u'\u014B', 'qwerty-ng-and-er', 'keyboard-btn pronunc-btn pronunc-nasal'],
        ['', '', '', '', '', '', '', 'qwerty-ng-and-er', 'ng-er-spacer'],
        ['ER', 'er', 'h', 'er', '', 'r_colored', u'\u025D', 'qwerty-ng-and-er', 'keyboard-btn pronunc-btn pronunc-r_colored'],
        ['AE', 'a', 'f', 'a', 'st', 'monophthong', u'\u00E6', 'combo-monophthong1', 'keyboard-btn pronunc-btn pronunc-monophthong'],
        ['AA', 'ah', 'f', 'a', 'ther', 'monophthong', u'\u0251', 'combo-monophthong1', 'keyboard-btn pronunc-btn pronunc-monophthong'],
        ['AO', 'aw', 'f', 'a', 'll', 'monophthong', u'\u0254', 'combo-monophthong1', 'keyboard-btn pronunc-btn pronunc-monophthong'],
        ['AH', 'uh', 'b', 'u', 't', 'monophthong', u'\u028C', 'combo-monophthong1', 'keyboard-btn pronunc-btn pronunc-monophthong'],
        ['AX', u'\u018F', 'disc', 'u', 's', 'monophthong', u'\u0259', 'combo-monophthong1', 'keyboard-btn pronunc-btn pronunc-monophthong'],
        ['EH', 'eh', 'r', 'e', 'd', 'monophthong', u'\u025B', 'combo-monophthong2', 'keyboard-btn pronunc-btn pronunc-monophthong'],
        ['IH', 'i', 'b', 'i', 'g', 'monophthong', u'\u026A', 'combo-monophthong2', 'keyboard-btn pronunc-btn pronunc-monophthong'],
        ['IY', 'ee', 'b', 'ee', '', 'monophthong', u'\u0069', 'combo-monophthong2', 'keyboard-btn pronunc-btn pronunc-monophthong'],
        ['UH', 'uu', 'b', 'oo', 'k', 'monophthong', u'\u028A', 'combo-monophthong2', 'keyboard-btn pronunc-btn pronunc-monophthong'],
        ['UW', 'ew', 'y', 'ou', '', 'monophthong', u'\u0075', 'combo-monophthong2', 'keyboard-btn pronunc-btn pronunc-monophthong'],
        ['AW', 'ao', 'h', 'ow', '', 'diphthong', u'\u0061\u028A', 'combo-diphthong', 'keyboard-btn pronunc-btn pronunc-diphthong'],
        ['AY', 'ai', 'm', 'y', '', 'diphthong', u'\u0061\u026A', 'combo-diphthong', 'keyboard-btn pronunc-btn pronunc-diphthong'],
        ['EY', 'ei', 's', 'ay', '', 'diphthong', u'\u025B\u026A', 'combo-diphthong', 'keyboard-btn pronunc-btn pronunc-diphthong'],
        ['OW', 'o', 'g', 'o', '', 'diphthong', u'\u006F\u028A', 'combo-diphthong', 'keyboard-btn pronunc-btn pronunc-diphthong'],
        ['OY', 'oi', 'b', 'oy', '', 'diphthong', u'\u0254\u026A', 'combo-diphthong', 'keyboard-btn pronunc-btn pronunc-diphthong'],
    ]

    return JsonResponse(keyboard_list, safe=False)


# ---- Add/Save new words to dictionary (via primeFaultSaveBtn in template JS)
def add_word_to_dict(request):
    print 'add_word_to_dict called'
    new_arpa_str = request.GET.get('new_arpa_str', '')
    print 'new_arpa_str: %s' % new_arpa_str
    new_word = request.GET.get('new_word', '')
    print 'new word: %s' % new_word

    new_arpa_list = new_arpa_str.split(' ')
    print new_arpa_list

    # variant_check, created = DictCMU.objects.get_or_create(
    #     entry__iexact=new_word)

    # if created:
    #     new_entry = variant_check
    # else:
    #     var_num = int(variant_check.num_of_variants) + 1
    #     # need to add num_of_variants to models
    #     # then make a routine to update the number of variants
    #     # for the other entries
    #     new_word_var = '%s(%s)' % (new_word, var_num)
    #     new_entry = DictCMU.objects.create(entry=new_word_var)

    # new_entry.source = '1'
    # new_entry.phonemes_no_num = new_arpa_str
    # new_entry.char_length = len(new_word)
    # new_entry.list_length = len(new_arpa_list)
    # new_entry.num_of_variants = var_num

    # new_entry.save()

    return HttpResponse(status=200)


# ---- Name func: takes arpabet phone and returns unicode symbols -----
def name_func(request):

    input_phone = request.GET.get('arpa_phone', '')

    arpa_deseret_U = {'IY': u'\uD801\uDC00', 'EY': u'\uD801\uDC01', 'AA': u'\uD801\uDC02', 'AO': u'\uD801\uDC03', 'OW': u'\uD801\uDC04', 'UW': u'\uD801\uDC05', 'IH': u'\uD801\uDC06', 'EH': u'\uD801\uDC07', 'AE': u'\uD801\uDC08', 'AH': u'\uD801\uDC0A', 'AX': u'\uD801\uDC0A', 'UH': u'\uD801\uDC0B', 'AY': u'\uD801\uDC0C', 'AW': u'\uD801\uDC0D', 'W': u'\uD801\uDC0E', 'Y': u'\uD801\uDC0F', 'HH': u'\uD801\uDC10', 'P': u'\uD801\uDC11', 'B': u'\uD801\uDC12', 'T': u'\uD801\uDC13', 'D': u'\uD801\uDC14', 'CH': u'\uD801\uDC15', 'JH': u'\uD801\uDC16', 'K': u'\uD801\uDC17', 'G': u'\uD801\uDC18', 'F': u'\uD801\uDC19', 'V': u'\uD801\uDC1A', 'TH': u'\uD801\uDC1B', 'DH': u'\uD801\uDC1C', 'S': u'\uD801\uDC1D', 'Z': u'\uD801\uDC1E', 'SH': u'\uD801\uDC1F', 'ZH': u'\uD801\uDC20', 'R': u'\uD801\uDC21', 'L': u'\uD801\uDC22', 'M': u'\uD801\uDC23', 'N': u'\uD801\uDC24', 'NG': u'\uD801\uDC25', 'OY': u'\uD801\uDC26', 'ER': u'\uD801\uDC21'}
    arpa_deseret_m = {'IY': u'\uD801\uDC28', 'EY': u'\uD801\uDC29', 'AA': u'\uD801\uDC2A', 'AO': u'\uD801\uDC2B', 'OW': u'\uD801\uDC2C', 'UW': u'\uD801\uDC2D', 'IH': u'\uD801\uDC2E', 'EH': u'\uD801\uDC2F', 'AE': u'\uD801\uDC30', 'AH': u'\uD801\uDC32', 'AX': u'\uD801\uDC32', 'UH': u'\uD801\uDC33', 'AY': u'\uD801\uDC34', 'AW': u'\uD801\uDC35', 'W': u'\uD801\uDC36', 'Y': u'\uD801\uDC37', 'HH': u'\uD801\uDC38', 'P': u'\uD801\uDC39', 'B': u'\uD801\uDC3A', 'T': u'\uD801\uDC3B', 'D': u'\uD801\uDC3C', 'CH': u'\uD801\uDC3D', 'JH': u'\uD801\uDC3E', 'K': u'\uD801\uDC3F', 'G': u'\uD801\uDC40', 'F': u'\uD801\uDC41', 'V': u'\uD801\uDC42', 'TH': u'\uD801\uDC43', 'DH': u'\uD801\uDC44', 'S': u'\uD801\uDC45', 'Z': u'\uD801\uDC46', 'SH': u'\uD801\uDC47', 'ZH': u'\uD801\uDC48', 'R': u'\uD801\uDC49', 'L': u'\uD801\uDC4A', 'M': u'\uD801\uDC4B', 'N': u'\uD801\uDC4C', 'NG': u'\uD801\uDC4D', 'OY': u'\uD801\uDC4E', 'ER': u'\uD801\uDC49'}
    arpa_greek_U = {'AA': u'\u0391', 'AE': u'\u0391', 'AH': u'\u039F\u03A5', 'AO': u'\u039F', 'AW': u'\u0391\u03A5', 'AX': u'\u0391', 'AY': u'\u0391\u0399', 'B': u'\u0392', 'CH': u'\u03A7', 'D': u'\u0394', 'DH': u'\u0398', 'EH': u'\u0395', 'ER': u'\u0395\u03A1', 'EY': u'\u0397', 'F': u'\u03A6', 'G': u'\u0393', 'HH': u'\u1FFE', 'IH': u'\u0399', 'IY': u'\u0399', 'JH': u'\u0393', 'K': u'\u039A', 'L': u'\u039B', 'M': u'\u039C', 'N': u'\u039D', 'NG': u'\u039D\u0393', 'OW': u'\u03A9', 'OY': u'\u039F\u0399', 'P': u'\u03A0', 'R': u'\u03A1', 'S': u'\u03A3', 'SH': u'\u03A3', 'T': u'\u03A4', 'TH': u'\u0398', 'UH': u'\u039F\u03A5', 'UW': u'\u039F\u03A5', 'V': u'\u0392', 'W': u'\u03A5', 'Y': u'\u0399', 'Z': u'\u0396', 'ZH': u'\u0396'}
    arpa_greek_m = {'AA': u'\u03B1', 'AE': u'\u03B1', 'AH': u'\u03BF\u03C5', 'AO': u'\u03BF', 'AW': u'\u03B1\u03B9', 'AX': u'\u03B1', 'AY': u'\u03B1\u03B9', 'B': u'\u03B2', 'CH': u'\u03C7', 'D': u'\u03B4', 'DH': u'\u03B8', 'EH': u'\u03B5', 'ER': u'\u03B5\u03C1', 'EY': u'\u03B7', 'F': u'\u03C6', 'G': u'\u03B3', 'HH': u'\u1FFE', 'IH': u'\u03B9', 'IY': u'\u03B9', 'JH': u'\u03B3', 'K': u'\u03BA', 'L': u'\u03BB', 'M': u'\u03BC', 'N': u'\u03BD', 'NG': u'\u03BD\u03B3', 'OW': u'\u03C9', 'OY': u'\u03BF\u03B9', 'P': u'\u03C0', 'R': u'\u03C1', 'S': u'\u03C2', 'SH': u'\u03C2', 'T': u'\u03C4', 'TH': u'\u03B8', 'UH': u'\u03BF\u03C5', 'UW': u'\u03BF\u03C5', 'V': u'\u03B2', 'W': u'\u03C5', 'Y': u'\u03B9', 'Z': u'\u03B6', 'ZH': u'\u03B6'}
    arpa_hebrew = {'B': u'\u05D1', 'G': u'\u05D2', 'JH': u'\u05D2\u05F3', 'D': u'\u05D3', 'HH': u'\u05D4', 'V': u'\u05D5', 'Z': u'\u05D6', 'ZH': u'\u05D6\u05F3', 'Y': u'\u05D9', 'K': u'\u05DB', 'L': u'\u05DC', 'M': u'\u05DE', 'N': u'\u05E0', 'S': u'\u05E1', 'F': u'\u05E4', 'P': u'\uFB44', 'CH': u'\u05E6\u05F3', 'R': u'\u05E8', 'SH': u'\u05E9', 'T': u'\u05D8', 'AY': u'\u05F0', 'AW': u'\u05D0\u05D5', 'EY': u'\u05F0', 'OW': u'\u05D5', 'OY': u'\u05F1', 'DH': u'\u05D3', 'TH': u'\u05EA', 'AE': u'', 'AA': u'', 'AX': u'', 'EH': u'', 'IY': u'\u05D9', 'IH': u'', 'AO': u'', 'UW': u'\u05D5', 'UH': u'\u05D5', 'AH': u'\u05D5', 'NG': u'\u05E0\u05D2', 'ER': u'\u05E8', 'W': u'\u05D5'}

    unic_out = [
        arpa_deseret_U[input_phone],
        arpa_deseret_m[input_phone],
        arpa_greek_U[input_phone],
        arpa_greek_m[input_phone],
        arpa_hebrew[input_phone],
    ]

    return JsonResponse(unic_out, safe=False)
