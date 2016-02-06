# The core code and some of the remaining comments for this factorization
# dictionary code is adapted from Mark Santesson's work which was generously
# released under the Creative Commons Attribution 3.0 Unported license
#
# minor modifications have been made to port the code to python3 and
# to make it work with slackbot - scott boone / sawall@github
#
# Original source reference:
# http://mostlyhighperformance.blogspot.com/2012/01/generating-anagrams-efficient-and-easy.html
#
# License reference: http://creativecommons.org/licenses/by/3.0/

from slackbot.bot import respond_to
import os
import sys
import collections
import functools


def prime_generator():
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41,
              43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]
    for p in primes:
        yield p


class ScrabbleGenerator:

    def __init__(self, dictionary_filename='/usr/share/dict/words'):
        self.dictionary_filename = dictionary_filename
        self.__loadDictionary()

    def __getPrime(self, c):
        return self.chars_list[ord(c) - ord('a')]

    def __getSignature(self, s):
        s = s.lower()
        sig = functools.reduce(lambda x, y: x * self.__getPrime(y),
                     [ch for ch in s if ord('a') <= ord(ch) <= ord('z')], 1)
        assert sig >= 1, repr(('Product of primes produced non-positive number', s, sig, [
                              (z, self.__getPrime(z)) for z in s if ord('a') <= ord(z) <= ord('z')]))
        return sig

    def __loadDictionary(self):
        # Reads the dictionary and constructs a dict that maps products of
        # prime numbers to words.
        all_lines = list()
        counts = dict([(chr(x), 0) for x in range(ord('a'), ord('z') + 1)])
        for line in open(self.dictionary_filename).readlines():
            # ditch single letters
            if (((len(line.strip()) > 1) or (line[0] == 'a' or line[0] == ['i'])) and (line.strip()[0].islower())):
                all_lines.append(line.strip())
                for c in line.lower():
                    if ord('a') <= ord(c) <= ord('z'):
                        counts[c] += 1

        primes = prime_generator()  # get the prime number generator
        chars_map = dict([(x, next(primes)) for x, y in
                          sorted(counts.items(), key=lambda i:i[1],
                                 reverse=True)])

        self.chars_list = [chars_map[chr(x)]
                           for x in range(ord('a'), ord('z') + 1)]

        self.sigs = collections.defaultdict(list)
        for word in all_lines:
            sig = self.__getSignature(word)
            if sig > 1:    # ignore lines without letters
                self.sigs[sig].append(word)

        self.sigs_keys = sorted(self.sigs.keys())

    def __getSignatureKeys(self):
        return self.sigs_keys

    def scrabbles(self, phrase_string, limit=2):
        all_keys = self.__getSignatureKeys()
        letters = self.__getSignature(phrase_string)

        # if a key can mod evenly into letters then it's a possible word match
        r = [x for x in all_keys if letters % x == 0]
        # generate list of all words that match valid keys and are above the
        # limit
        words = [self.sigs[row]
                 for row in r if len(self.sigs[row][0]) >= limit]
        # flatten and reverse
        return [v for sublist in words for v in sublist][::-1]


@respond_to('scrabble (.*)')
def scrabble(message, thing):
    message.reply('pondering \"%s\", hold please...' % thing)
    sg = ScrabbleGenerator()
    r = sg.scrabbles(thing)
    message.reply('scrabbles of \"%s\":\n%s' % (thing,
        " ".join(map(lambda x: str(x).upper(), r))))


@respond_to('scrabble5 (.*)')
def scrabble5(message, thing):
    message.reply('pondering \"%s\", hold please...' % thing)
    sg = ScrabbleGenerator()
    r = sg.scrabbles(thing, 5)
    message.reply('scrabbles 5+ letters long of \"%s\":\n%s' % (thing,
        " ".join(map(lambda x: str(x).upper(), r))))
