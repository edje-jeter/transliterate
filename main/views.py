import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response, redirect
from django.template import RequestContext

from main.models import DictCMU

from main.forms import EnglishInputForm


def json_response(request):

    # read data from input box
    input_string = request.GET.get('input', '')
    print "input_string: %s" % input_string

    # Make a map that shows capitals, miniscules, apostrophes, and non-letters
    input_length = len(input_string)

    input_map1 = []
    for i in range(0, input_length):
        # test if char is a capital letter and, thus, part of a word
        if ord(input_string[i]) > 64 and ord(input_string[i]) < 91:
            input_map1.append("C")
        # test if char is a miniscule letter and, thus, part of a word
        elif ord(input_string[i]) > 96 and ord(input_string[i]) < 123:
            input_map1.append("m")
        # test for apostrophes (which will be dealt with below)
        elif input_string[i] == "'":
            input_map1.append("a")
        # for now we'll say everything else is not part of a word
        # we'll probably have to deal with hyphens at some point
        else:
            input_map1.append(input_string[i])

    # Test if char is a non-terminal apostrophe (and, thus, part
    # of a word) or a single-quote mark or terminal apostrophe
    # (and, thus, not part of a word)
    for i in range(0, input_length):
        # find the apostrophe marks
        if input_map1[i] == "a":
            # test if apostrophe starts or ends the string
            if i == 0 or i == input_length - 1:
                input_map1[i] = "'"
            # test if apostrophe is part of a word (ie, has letters on both sides)
            elif input_map1[i-1] in ("C", "m") and input_map1[i+1] in ("C", "m"):
                input_map1[i] = input_map1[i+1]
            # every other apostrophe is not part of a word
            else:
                input_map1[i] = "'"
    print "input_map1 (joined): %s" % ''.join(input_map1)

    # Finalize the map, categorizing words as all-caps (CC),
    # initial-cap (Cm), and no-caps (mm)
    # Also make a list of words to be transliterated.
    input_map2 = []
    word_index = []
    for i in range(0, input_length):
        # put non-words directly into the final map
        if input_map1[i] not in ("C", "m"):
            input_map2.append(input_map1[i])
            # record index for the end of a word
            # print "im1[i-1]: %s" % input_map1[i-1]
            if i == 0:
                pass
            elif input_map1[i-1] in ("C", "m"):
                word_index.append(i)
        # everything else is part of a word
        else:
            # find first-letters and put them in map
            # record the index for the start of the word
            if i == 0 or input_map1[i-1] not in ("C", "m"):
                input_map2.append(input_map1[i])
                word_index.append(i)
            # find second-letters (if present) and put them in map
            elif i == 1 and input_map1[0] in ("C", "m"):
                input_map2[0] = input_map1[0] + input_map1[1]
            elif input_map1[i-2] not in ("C", "m") and input_map1[i-1] in ("C", "m"):
                cur_index = len(input_map2) - 1
                let_1 = input_map2[cur_index]
                let_2 = input_map1[i]
                input_map2[cur_index] = let_1 + let_2
            # Check if last char of string is a letter and make it end of word
            elif i == len(input_map1) - 1:
                word_index.append(i+1)
            # ignore all other letters [remember that at this stage
            # we're ignoring the possibility of mixing upper and
            # lower case letters except init caps]

    print "input_map2 (joined): %s" % ''.join(input_map2)
    print "word_index: %s" % word_index

    # generate list of words to be transliterated
    word_list = []
    word_count = len(word_index)
    for i in range(0, word_count, 2):
        start = word_index[i]
        stop = word_index[i+1]
        word_list.append(input_string[start:stop])
    print "word_list: %s" % word_list

    # Get Arpabet correlations for each word in word_list
    arpa_phonemes = {}
    word_num = 0
    for word in word_list:
        # Since the word might not be in the dictionary, we
        # try to fail softly
        try:
            arpa_output = DictCMU.objects.get(entry__iexact=word)

            # the db stores pronunc info as unicode; we force it to str
            arpa_phon_str = str(arpa_output.phonemes)

            # remove accent characters
            char_to_remove = ['0', '1', '2']
            arpa_phon_clean = arpa_phon_str.translate(None, ''.join(char_to_remove))

            # turn the string into a list
            arpa_phonemes[word] = arpa_phon_clean.split()

        except Exception, e:
            arpa_phonemes[word] = "NO MATCH"

        word_num += 1

    print "arpa_phonemes: %s" % arpa_phonemes

    # get unicode correlations
    arpa_correlation_U = {'IY': u'\uD801\uDC00', 'EY': u'\uD801\uDC01', 'AA': u'\uD801\uDC02', 'AO': u'\uD801\uDC03', 'OW': u'\uD801\uDC04', 'UW': u'\uD801\uDC05', 'IH': u'\uD801\uDC06', 'EH': u'\uD801\uDC07', 'AE': u'\uD801\uDC08', 'AH': u'\uD801\uDC0A', 'UH': u'\uD801\uDC0B', 'AY': u'\uD801\uDC0C', 'AW': u'\uD801\uDC0D', 'W': u'\uD801\uDC0E', 'Y': u'\uD801\uDC0F', 'HH': u'\uD801\uDC10', 'P': u'\uD801\uDC11', 'B': u'\uD801\uDC12', 'T': u'\uD801\uDC13', 'D': u'\uD801\uDC14', 'CH': u'\uD801\uDC15', 'JH': u'\uD801\uDC16', 'K': u'\uD801\uDC17', 'G': u'\uD801\uDC18', 'F': u'\uD801\uDC19', 'V': u'\uD801\uDC1A', 'TH': u'\uD801\uDC1B', 'DH': u'\uD801\uDC1C', 'S': u'\uD801\uDC1D', 'Z': u'\uD801\uDC1E', 'SH': u'\uD801\uDC1F', 'ZH': u'\uD801\uDC20', 'R': u'\uD801\uDC21', 'L': u'\uD801\uDC22', 'M': u'\uD801\uDC23', 'N': u'\uD801\uDC24', 'NG': u'\uD801\uDC25', 'OY': u'\uD801\uDC26', 'ER': u'\uD801\uDC21'}
    arpa_correlation_m = {'IY': u'\uD801\uDC28', 'EY': u'\uD801\uDC29', 'AA': u'\uD801\uDC2A', 'AO': u'\uD801\uDC2B', 'OW': u'\uD801\uDC2C', 'UW': u'\uD801\uDC2D', 'IH': u'\uD801\uDC2E', 'EH': u'\uD801\uDC2F', 'AE': u'\uD801\uDC30', 'AH': u'\uD801\uDC32', 'UH': u'\uD801\uDC33', 'AY': u'\uD801\uDC34', 'AW': u'\uD801\uDC35', 'W': u'\uD801\uDC36', 'Y': u'\uD801\uDC37', 'HH': u'\uD801\uDC38', 'P': u'\uD801\uDC39', 'B': u'\uD801\uDC3A', 'T': u'\uD801\uDC3B', 'D': u'\uD801\uDC3C', 'CH': u'\uD801\uDC3D', 'JH': u'\uD801\uDC3E', 'K': u'\uD801\uDC3F', 'G': u'\uD801\uDC40', 'F': u'\uD801\uDC41', 'V': u'\uD801\uDC42', 'TH': u'\uD801\uDC43', 'DH': u'\uD801\uDC44', 'S': u'\uD801\uDC45', 'Z': u'\uD801\uDC46', 'SH': u'\uD801\uDC47', 'ZH': u'\uD801\uDC48', 'R': u'\uD801\uDC49', 'L': u'\uD801\uDC4A', 'M': u'\uD801\uDC4B', 'N': u'\uD801\uDC4C', 'NG': u'\uD801\uDC4D', 'OY': u'\uD801\uDC4E', 'ER': u'\uD801\uDC49'}

    unic_out = []
    ticker = 0
    for inp in input_map2:
        if inp in ("CC", "C", "Cm", "mm", "m"):
            # print "a_p[w_l[t]]: %s" % arpa_phonemes[word_list[ticker]]
            if arpa_phonemes[word_list[ticker]] == "NO MATCH":
                a = "."*len(word_list[ticker])
                unic_out.append(a)
                ticker += 1
            elif inp == "CC" or inp == "C":
                for phone in arpa_phonemes[word_list[ticker]]:
                    unic_out.append(arpa_correlation_U[phone])
                ticker += 1
            elif inp == "mm" or inp == "m":
                for phone in arpa_phonemes[word_list[ticker]]:
                    unic_out.append(arpa_correlation_m[phone])
                ticker += 1
                # print "ticker: %s" % ticker
            elif inp == "Cm":
                for i in range(0, len(arpa_phonemes[word_list[ticker]])):
                    if i == 0:
                        unic_out.append(arpa_correlation_U[arpa_phonemes[word_list[ticker]][i]])
                    else:
                        unic_out.append(arpa_correlation_m[arpa_phonemes[word_list[ticker]][i]])
                ticker += 1
                print "ticker: %s" % ticker
        else:
            unic_out.append(inp)
    print "unic_out: %s" % unic_out

    # unic_str = ''.join(unic_out)
    # print "unic_str: %s" % unic_str

    # object_list = []
    # for obj in objects:
    #     object_list.append(obj.phonemes)

    return JsonResponse(unic_out, safe=False)


def input_output(request):
    # the correlation between the Arpabet and the Deseret script.
    # Note: This is a provisional correlation for early proof-of-concept
    # work; it has serious flaws in the correlations.

    arpa_correlation_U = {'IY': u'\uD801\uDC00',
                          'EY': u'\uD801\uDC01',
                          'AA': u'\uD801\uDC02',
                          'AO': u'\uD801\uDC03',
                          'OW': u'\uD801\uDC04',
                          'UW': u'\uD801\uDC05',
                          'IH': u'\uD801\uDC06',
                          'EH': u'\uD801\uDC07',
                          'AE': u'\uD801\uDC08',
                          'AH': u'\uD801\uDC0A',
                          'UH': u'\uD801\uDC0B',
                          'AY': u'\uD801\uDC0C',
                          'AW': u'\uD801\uDC0D',
                          'W': u'\uD801\uDC0E',
                          'Y': u'\uD801\uDC0F',
                          'HH': u'\uD801\uDC10',
                          'P': u'\uD801\uDC11',
                          'B': u'\uD801\uDC12',
                          'T': u'\uD801\uDC13',
                          'D': u'\uD801\uDC14',
                          'CH': u'\uD801\uDC15',
                          'JH': u'\uD801\uDC16',
                          'K': u'\uD801\uDC17',
                          'G': u'\uD801\uDC18',
                          'F': u'\uD801\uDC19',
                          'V': u'\uD801\uDC1A',
                          'TH': u'\uD801\uDC1B',
                          'DH': u'\uD801\uDC1C',
                          'S': u'\uD801\uDC1D',
                          'Z': u'\uD801\uDC1E',
                          'SH': u'\uD801\uDC1F',
                          'ZH': u'\uD801\uDC20',
                          'R': u'\uD801\uDC21',
                          'L': u'\uD801\uDC22',
                          'M': u'\uD801\uDC23',
                          'N': u'\uD801\uDC24',
                          'NG': u'\uD801\uDC25',
                          'OY': u'\uD801\uDC26',
                          'ER': u'\uD801\uDC21',
                          }

    arpa_correlation_m = {'IY': u'\uD801\uDC28',
                          'EY': u'\uD801\uDC29',
                          'AA': u'\uD801\uDC2A',
                          'AO': u'\uD801\uDC2B',
                          'OW': u'\uD801\uDC2C',
                          'UW': u'\uD801\uDC2D',
                          'IH': u'\uD801\uDC2E',
                          'EH': u'\uD801\uDC2F',
                          'AE': u'\uD801\uDC30',
                          'AH': u'\uD801\uDC32',
                          'UH': u'\uD801\uDC33',
                          'AY': u'\uD801\uDC34',
                          'AW': u'\uD801\uDC35',
                          'W': u'\uD801\uDC36',
                          'Y': u'\uD801\uDC37',
                          'HH': u'\uD801\uDC38',
                          'P': u'\uD801\uDC39',
                          'B': u'\uD801\uDC3A',
                          'T': u'\uD801\uDC3B',
                          'D': u'\uD801\uDC3C',
                          'CH': u'\uD801\uDC3D',
                          'JH': u'\uD801\uDC3E',
                          'K': u'\uD801\uDC3F',
                          'G': u'\uD801\uDC40',
                          'F': u'\uD801\uDC41',
                          'V': u'\uD801\uDC42',
                          'TH': u'\uD801\uDC43',
                          'DH': u'\uD801\uDC44',
                          'S': u'\uD801\uDC45',
                          'Z': u'\uD801\uDC46',
                          'SH': u'\uD801\uDC47',
                          'ZH': u'\uD801\uDC48',
                          'R': u'\uD801\uDC49',
                          'L': u'\uD801\uDC4A',
                          'M': u'\uD801\uDC4B',
                          'N': u'\uD801\uDC4C',
                          'NG': u'\uD801\uDC4D',
                          'OY': u'\uD801\uDC4E',
                          'ER': u'\uD801\uDC49',
                          }

    context = {}

    form1 = EnglishInputForm()

    context['form_1'] = form1

    if request.method == 'POST':
        form1 = EnglishInputForm(request.POST)
        context['form_1'] = form1
        if form1.is_valid():
            # read data from form
            english_input_v = form1.cleaned_data['english_input_f']
            context['english_input_v'] = english_input_v

            # Make a map that shows capitals, miniscules, apostrophes, and non-letters
            input_length = len(english_input_v)

            input_map1 = []
            for i in range(0, input_length):
                # test if char is a capital letter and, thus, part of a word
                if ord(english_input_v[i]) > 64 and ord(english_input_v[i]) < 91:
                    input_map1.append("C")
                # test if char is a miniscule letter and, thus, part of a word
                elif ord(english_input_v[i]) > 96 and ord(english_input_v[i]) < 123:
                    input_map1.append("m")
                # test for apostrophes (which will be dealt with below)
                elif english_input_v[i] == "'":
                    input_map1.append("a")
                # for now we'll say everything else is not part of a word
                # we'll probably have to deal with hyphens at some point
                else:
                    input_map1.append(english_input_v[i])

            # test if char is a non-terminal apostrophe (and, thus, part
            # of a word) or a single-quote mark or terminal apostrophe
            # (and, thus, not part of a word)
            for i in range(0, input_length):
                # find the apostrophe marks
                if input_map1[i] == "a":
                    # test if apostrophe starts or ends the string
                    if i == 0 or i == input_length - 1:
                        input_map1[i] = "'"
                    # test if apostrophe is part of a word (ie, has letters on both sides)
                    elif input_map1[i-1] in ("C", "m") and input_map1[i+1] in ("C", "m"):
                        input_map1[i] = input_map1[i+1]
                    # every other apostrophe is not part of a word
                    else:
                        input_map1[i] = "'"
            print "input_map1 (joined): %s" % ''.join(input_map1)
            print input_map1

            context['input_map1'] = input_map1

            # Finalize the map, categorizing words as all-caps (CC),
            # initial-cap (Cm), and no-caps (mm)
            # Also make a list of words to be transliterated.
            input_map2 = []
            word_index = []
            for i in range(0, input_length):
                # put non-words directly into the final map
                if input_map1[i] not in ("C", "m"):
                    input_map2.append(input_map1[i])
                    # record index for the end of a word
                    # print "im1[i-1]: %s" % input_map1[i-1]
                    if i == 0:
                        pass
                    elif input_map1[i-1] in ("C", "m"):
                        word_index.append(i)
                # everything else is part of a word
                else:
                    # find first-letters and put them in map
                    # record the index for the start of the word
                    if i == 0 or input_map1[i-1] not in ("C", "m"):
                        input_map2.append(input_map1[i])
                        word_index.append(i)
                    # find second-letters (if present) and put them in map
                    elif i == 1 and input_map1[0] in ("C", "m"):
                        input_map2[0] = input_map1[0] + input_map1[1]
                    elif input_map1[i-2] not in ("C", "m") and input_map1[i-1] in ("C", "m"):
                        cur_index = len(input_map2) - 1
                        let_1 = input_map2[cur_index]
                        let_2 = input_map1[i]
                        input_map2[cur_index] = let_1 + let_2
                    # Check if last char of string is a letter and make it end of word
                    elif i == len(input_map1) - 1:
                        word_index.append(i+1)
                    # ignore all other letters [remember that at this stage
                    # we're ignoring the possibility of mixing upper and
                    # lower case letters except init caps]

            print input_map2
            print "input_map2 (joined): %s" % ''.join(input_map2)
            print "word_index: %s" % word_index

            # generate list of words to be transliterated
            word_list = []
            word_count = len(word_index)
            for i in range(0, word_count, 2):
                start = word_index[i]
                stop = word_index[i+1]
                word_list.append(english_input_v[start:stop])
            print "word_list: %s" % word_list

            context['word_list'] = word_list

            # get Arpabet correlations for each word in word_list
            arpa_phonemes = {}
            word_num = 0
            for word in word_list:
                # Since the word might not be in the dictionary, we
                # try to fail softly
                try:
                    arpa_output = DictCMU.objects.get(entry__iexact=word)

                    # the db stores pronunc info as unicode; we force it to str
                    arpa_phon_str = str(arpa_output.phonemes)

                    # remove accent characters
                    char_to_remove = ['0', '1', '2']
                    arpa_phon_clean = arpa_phon_str.translate(None, ''.join(char_to_remove))

                    # turn the string into a list
                    arpa_phonemes[word] = arpa_phon_clean.split()

                except Exception, e:
                    arpa_phonemes[word] = "NO MATCH"

                word_num += 1

            context['arpa_phonemes'] = arpa_phonemes
            print "arpa_phonemes: %s" % arpa_phonemes

            # get unicode correlations
            unic_out = []
            ticker = 0
            for inp in input_map2:
                if inp in ("CC", "C", "Cm", "mm", "m"):
                    print "a_p[w_l[t]]: %s" % arpa_phonemes[word_list[ticker]]
                    if arpa_phonemes[word_list[ticker]] == "NO MATCH":
                        a = "."*len(word_list[ticker])
                        unic_out.append(a)
                        ticker += 1
                    elif inp == "CC" or inp == "C":
                        for phone in arpa_phonemes[word_list[ticker]]:
                            unic_out.append(arpa_correlation_U[phone])
                        ticker += 1
                    elif inp == "mm" or inp == "m":
                        for phone in arpa_phonemes[word_list[ticker]]:
                            unic_out.append(arpa_correlation_m[phone])
                        ticker += 1
                        print "ticker: %s" % ticker
                    elif inp == "Cm":
                        for i in range(0, len(arpa_phonemes[word_list[ticker]])):
                            if i == 0:
                                unic_out.append(arpa_correlation_U[arpa_phonemes[word_list[ticker]][i]])
                            else:
                                unic_out.append(arpa_correlation_m[arpa_phonemes[word_list[ticker]][i]])
                        ticker += 1
                        print "ticker: %s" % ticker
                else:
                    unic_out.append(inp)
            print "unic_out: %s" % unic_out
            context['unic_out'] = unic_out

            unic_str = ''.join(unic_out)
            print "unic_str: %s" % unic_str
            context['unic_str'] = unic_str

    context['output_intermed'] = "placeholding test text"

    return render_to_response('input_output.html', context,
                              context_instance=RequestContext(request))
