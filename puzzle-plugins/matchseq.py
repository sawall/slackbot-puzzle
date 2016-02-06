# various ways to help find words that match arbitrary ciphertext sequences
# (c) scott boone / sawall@github
#
# license ref: http://creativecommons.org/licenses/by/4.0/

from slackbot.bot import respond_to
import os
import sys
import collections
import string
import copy


class DictionaryWords:

    def __init__(self, dictionary_filename='/usr/share/dict/words'):
        self.dictionary_filename = dictionary_filename
        self.word_list = []
        for line in open(self.dictionary_filename).readlines():
            self.word_list.append(line.strip())

    def word_generator(self):
        for line in open(self.dictionary_filename).readlines():
            # remove uppercase words and strip out single letter words other
            # than 'a' and 'I':
            if (((len(line.strip()) > 1) or (line[0] == 'a' or line[0] == ['i']))
                    and (line.strip()[0].islower())):
                yield(line.strip())
        yield "!!!EOF!!!"

    def word_list(self):
        return self.word_list


def matchseq(word, seq):
    """ 
        compares to letter sequences to see if they pattern match
        e.g., 'COLOUR' will match 'ABCBDE'
    """
    if len(word) != len(seq):
        return False
    word = word.upper()
    seq = seq.upper()
    seqmap = {}
    for i in range(len(word)):
        # first check to see if word[i] already has a mapping
        if word[i] in seqmap.values():
            if seq[i] not in seqmap:
                # something else maps to word[i]
                return False
            elif seqmap[seq[i]] != word[i]:
                # seq[i] maps to something other than word[i]
                return False
            else:
                # seq[i] maps to word[i]
                pass
        # next make sure we don't already have seq[i]
        elif seq[i] in seqmap:
            # seq[i] exists and must map to something other than word[i]
            return False
        else:
            # we can safely add word[i] to the map
            seqmap[seq[i]] = word[i]
    return True


def lettergen():
    uc = string.uppercase
    i = 0
    while i < len(uc):
        yield uc[i]
        i += 1


def normalize_word(word):
    """
        Normalizes words by making it uppercase then substituting using A
        as the first unique letter, B as the second, and so on.
    """
    lg = lettergen()
    wordmap = {}
    out = ""
    for c in word.upper():
        if c not in wordmap:
            wordmap[c] = next(lg)
        out += wordmap[c]
    return out


def validword(seq, word, substmap={}):
    """
        Checks to see if a word is possible a possible match to a sequence,
        based on a substitution map. assumes words are same length, etc
        substmap maps ciphtertext to plaintext (seq to word)
        returns an updated substitution map or {} to indicate despair
    """
    i = 0
    newmap = copy.deepcopy(substmap)
    while i < len(word):
        if seq[i] in substmap:
            if substmap[seq[i]] != word[i]:
                return {}  # no dice
        else:
            # add mappings in both directions for a substitution cipher
            newmap[seq[i]] = word[i]
            newmap[word[i]] = seq[i]
        i += 1
    return newmap


def findmatches(phrase_list, outlst, dw, subst_map={}, outstr=""):
    """
        resursively iterates through a phrase list (which contains ordered
        mappings of a word to a list of possible words) and slaps validated
        word combinations into outlst
    """
    if len(phrase_list) == 0:
        outlst.append(outstr[:-1])
        # print outstr
        return
    for word in phrase_list[0][1]:  # iterate over possible mappings of first word
        word = word.upper()
        newmap = validword(word, phrase_list[0][0], subst_map)  # uses deepcopy
        if newmap != {}:
            # only go deeper if we're onto something promising
            findmatches(phrase_list[1:], outlst, dw,
                        newmap, outstr + word + " ")

@respond_to('matchword (.*)')
def matchword(message, thing):
    out = ""
    dw = DictionaryWords()
    dg = dw.word_generator()
    n = next(dg)
    while (n != "!!!EOF!!!"):
        if matchseq(n, thing):
            out += " " + n
        n = next(dg)
    message.reply('words that match the pattern \"%s\":\n%s' % (thing, out))


@respond_to('matchphrase (.*)')
def matchphrase(message, thing):
    # create a map that normalizes all dictionary words
    normalized_dict = {}
    dw = DictionaryWords(
        dictionary_filename='puzzle-plugins/google-10000-english.txt')
    dg = dw.word_generator()
    n = next(dg)
    while (n != "!!!EOF!!!"):
        if normalize_word(n) in normalized_dict:
            normalized_dict[normalize_word(n)].append(n)
        else:
            normalized_dict[normalize_word(n)] = [n]
        n = next(dg)
    # sample dict item: {'ABCDEFABGC': ['antiplanet', 'literalist']}
    message.reply('generated %s unique patterns from the dictionary. now analyzing \"%s\" for potential matches with the assumption that substitutions are 1:1. hold please...' % (
        str(len(normalized_dict)), thing))

    # map input words to lists of possible dictionary matches
    phrase_list = []
    for word in thing.split():
        # strip non-alpha charactersatch
        word = ''.join(e for e in word if e.isalpha())
        phrase_list.append((word.upper(), normalized_dict[
                           normalize_word(word.upper())]))

        # optimization: resort list starting with fewest to most possible word
        # matches

    outlst = []
    findmatches(phrase_list, outlst, dw)
    message.reply('matches are as follows:\n%s' % ', '.join(outlst))

# TODO:
# find combinations of words
# how best to do? normalize and then build a dictionary
# map everything to an A-Z map
# then we can cross-compare words

# TODO:
# find a dict word that matches sequence with unknowns
# e.g., CO?O?R ==> COLOUR
