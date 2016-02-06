# The core code and some of the remaining comments for this factorization
# anagram code is adapted from Mark Santesson's work which was generously
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


class AnagramGenerator:

    def __init__(self, dictionary_filename='/usr/share/dict/words'):
        self.dictionary_filename = dictionary_filename
        self.__loadDictionary()

    def __getPrime(self, c):
        '''Returns prime representative of character c.'''
        return self.chars_list[ord(c) - ord('a')]

    def __getSignature(self, s):
        '''Returns integer that represents character combination in string s.'''
        s = s.lower()
        sig = functools.reduce(lambda x, y: x * self.__getPrime(y),
                     [ch for ch in s if ord('a') <= ord(ch) <= ord('z')], 1)
        assert sig >= 1, repr(('Product of primes produced non-positive number', s, sig, [
                              (z, self.__getPrime(z)) for z in s if ord('a') <= ord(z) <= ord('z')]))
        return sig

    def __loadDictionary(self):
        '''Load a dictionary from the given input file. The file
        should have one word per line.'''

        # count characters in the dictionary in order to decide how to
        # assign primes to characters.
        all_lines = list()
        counts = dict([(chr(x), 0) for x in range(ord('a'), ord('z') + 1)])
        for line in open(self.dictionary_filename).readlines():
            # remove uppercase words and strip out single letter words other
            # than 'a' and 'I':
            if (((len(line.strip()) > 1) or (line[0] == 'a' or line[0] == ['i']))
                    and (line.strip()[0].islower())):
                all_lines.append(line.strip())
                for c in line.lower():
                    if ord('a') <= ord(c) <= ord('z'):
                        counts[c] += 1

        # creat mapping of lower case letter to prime numbers, based on
        # frequency (this keeps products for commonly used letters smaller)
        primes = prime_generator()
        chars_map = dict([(x, next(primes)) for x, y in
                          sorted(counts.items(), key=lambda i:i[1],
                                 reverse=True)])

        # recast primes into a list for faster lookups (index is alphabetical)
        self.chars_list = [chars_map[chr(x)]
                           for x in range(ord('a'), ord('z') + 1)]

        # calculate product of letters for dictionary words
        self.sigs = collections.defaultdict(list)
        for word in all_lines:
            sig = self.__getSignature(word)
            if sig > 1:    # ignore lines without letters
                self.sigs[sig].append(word)

        # sort signature keys for speed
        self.sigs_keys = sorted(self.sigs.keys())

    def __getSignatureKeys(self):
        '''Returns the sorted list of all signature keys. This is
        used to populate a list of all available words.'''
        return self.sigs_keys

    def formulateAnagramPhraseCombo(self, res):
        '''Render an anagram "phrase" into text for display. Each key
        is separate by double spaces, and each key displays as a comma
        separated list of the words choices.'''
        return "  ".join([','.join(self.sigs[s]) for s in res])

    def __solveAnagramPhrase(self, letters, unreduced_keys, start=0,
                             so_far=[]):
        '''This is the recursive function that helps produce anagrams.
        It should not be called directly.'''

        # letters: Product of signatures of letters remaining.
        # unreduced_keys: Keys representing items in the dictionary
        #    that can non necessarily be reached by the remaining
        #    letters.
        # start: The index of unreduced_keys to start considering.
        #    keys before this do not need to be considered in
        #    combination with this pick because earlier keys
        #    will be considered separately and they will consider
        #    combining with this pick as part of their recursion.
        #    The start value should be considered again in case
        #    the same key can be used multiple times.
        # so_far: A list containing the keys that have been picked
        #    so far in this chain of recursions.

        if letters == 1:
            return [so_far]

        # Filter list of keys to remove any that can no longer
        # be constructed using some of the input letters.
        reduced_keys = [x for x in unreduced_keys[start:] if letters % x == 0]
        result = []

        # Recurse on all items remaining in the dictionary.
        for index, sig in enumerate(reduced_keys):
            remaining_letters = letters // sig
            result += self.__solveAnagramPhrase(
                letters=remaining_letters,
                unreduced_keys=reduced_keys,
                start=index,
                so_far=so_far + [sig],
            )

        return result

    def anagrams(self, phrase_string):
        '''This function takes an input phrase string and returns
        a list of all anagrams that can be generated from it. The
        return value is a list of lists of lists. The inner lists
        represent the individual words which are interchangeable
        in an anagram. For instance, "tarp" and "trap" are
        anagrams of each other. Whenever one can be used, the
        other can substitute. They will be presented together
        in the innermost list. An example output for "lumberjack"
        might be:
        [ [ ['me'], ['bark'], ['Cluj'] ],
          [ ['me'], ['blur','burl'], ['jack'], ],
          [ ['be'], ['mark'], ['Cluj'] ]
          [ ['am'], ['jerk'], ['club'] ]
          [ ['elm','Mel'], ['jar'], ['buck'] ]
          ...
          ]
        '''
        all_keys = self.__getSignatureKeys()

        r = self.__solveAnagramPhrase(
            self.__getSignature(phrase_string),
            all_keys,
        )

        r = [[self.sigs[s] for s in row] for row in r]
        return r


@respond_to('anagram (.*)')
def anagram(message, thing):
    message.reply('pondering \"%s\", hold please...' % thing)
    ag = AnagramGenerator()
    r = ag.anagrams(thing)
    # print r
    message.reply('top anagrams of \"%s\":\n%s' % (thing,
        "\n".join("  ".join(map((lambda x: str.translate(str(x).upper(), str.maketrans(' ', '/', "[],\'"))), l)) for l in r[-20::])))
