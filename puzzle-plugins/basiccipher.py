# some basic ciphertext analysis tools
# (c) scott boone / sawall@github
#
# license ref: http://creativecommons.org/licenses/by/4.0/

from slackbot.bot import respond_to
import string
import operator

@respond_to('rotn (.*)')
def rotn(message, thing):
    base = string.ascii_lowercase + string.ascii_uppercase
    out = "```\n"
    for i in range(len(base)):
        rotn = str.maketrans(base, base[i::] + base[0:i:])
        out += "  rot" + str(i) + ": " + str.translate(thing, rotn) + "\n"
    message.reply(out + "```")

def checkpattern(pattern, word):
    word = str.upper(word)
    if len(pattern) != len(word):
        return False
    for i in range(len(pattern)):
        if pattern[i] != '?':
            if pattern[i] != word[i]:
                return False
    return word

# looks for matching word in dict with ? for unknown; YO?R -> YOUR
# TODO: seems to miss some things that might end with 'S', e.g., COATS
@respond_to('matchwildcard (.*)')
def wordpattern(message, pattern):
    pattern = str.upper(pattern)
    dictionary_filename = '/usr/share/dict/words'
    outstr = ""
    for line in open(dictionary_filename).readlines():
        foo = checkpattern(pattern, line.strip())
        if foo:
            outstr += foo + " "
    message.reply("words matching that pattern: " + outstr)

# count frequencies of letters in a word or phrase
@respond_to('freq (.*)')
def freq(message, thing):
    freqs = {}
    for c in thing:
        if c in freqs:
            freqs[c] += 1
        else:
            freqs[c] = 1
    freqsort = sorted(freqs.items(), key=operator.itemgetter(1), reverse=True)
    message.reply("here's your frequencies: " + str(freqsort))

# TODO: atbash
# TODO: keyed caesar

# calculate frequency of letters and then sub naively based on english
# letter frequency
@respond_to('freqsubst (.*)')
def freqsubst(message, thing):
    cache = thing
    english_common = "etaoinshrdlcumwfgypbvkjxqz"
    freqs = {}
    # first we build a frequency table
    for c in thing.lower():
        if c in english_common:
            if c in freqs:
                freqs[c] += 1
            else:
                freqs[c] = 1
    # build translation map
    ordered_thing = ""
    for c in sorted(freqs.items(), key=operator.itemgetter(1), reverse=True):
        ordered_thing += c[0]
    for c in english_common:
        if c not in ordered_thing:
            ordered_thing += c

    attempt = str.translate(thing,
                               str.maketrans(ordered_thing + ordered_thing.upper(),
                                             english_common + english_common.upper()))
    out = "attempting to substitute based on english frequencies...\n" +\
            "freqs: " + ordered_thing.upper() + " mapped to: " + english_common.upper() + "\n" +\
            "==> " + attempt
    message.reply(out)


def meantup(lst):
    if len(lst) > 0:
        nums = []
        for i in lst:
            nums.append(i[1])
        # print nums
        return sum(nums) / float(len(nums))
    return 0


# calculate frequency of letters and then sub first letters and other letters
# based on english frequencies
@respond_to('freqsubst2 (.*)')
def freqsubst2(message, thing):
    cache = thing
    # frequency order for first letters and letters in general
    english_first = "sacmprtbfgdhinelowuvjkqyzx"
    english_common = "etaoinshrdlcumwfgypbvkjxqz"
    # first we build two frequency tables
    freqs_first = {}
    freqs_all = {}
    first = True
    for c in thing.lower():
        if c in english_common:
            if first:
                if c in freqs_first:
                    freqs_first[c] += 1
                else:
                    freqs_first[c] = 1
                first = False
            if c in freqs_all:
                freqs_all[c] += 1
            else:
                freqs_all[c] = 1
        else:
            first = True  # reset first when there's non-alphanumeric
    # build translation map
    ordered_thing = ""
    sort_first = sorted(freqs_first.items(),
                        key=operator.itemgetter(1), reverse=True)
    sort_all = sorted(freqs_all.items(),
                      key=operator.itemgetter(1), reverse=True)
    firstmean = meantup(freqs_first.items())
    for c in sort_first:
        # don't take ALL the first letters
        if freqs_first[c[0]] > freqs_first[sort_first[0][0]] / firstmean:
            ordered_thing += c[0]
    # print "ordered from first letters: " + ordered_thing
    for c in sort_all:
        if c[0] not in ordered_thing:
            ordered_thing += c[0]
    # print "ordered from other letters: " + ordered_thing
    for c in english_common:
        if c not in ordered_thing:
            ordered_thing += c
    # print english_common + " " + ordered_thing
    cachemap = (ordered_thing, english_common)
    attempt = str.translate(thing,
                               str.maketrans(ordered_thing + ordered_thing.upper(),
                                         english_common + english_common.upper()))
    out = "attempting a more sneaky substitution using first-letter frequencies...\n" +\
            "freqs: " + ordered_thing.upper() + " mapped to: " + english_common.upper() + "\n" +\
        "==> " + attempt
    message.reply(out)

# in the above code, do I actually combine everything nicely or am I keeping two
# separate lists? I suspect I may have munged something

# frequency enhancements:
# make guesses using common 2/3 letter words
# make guesses using common 2/3 letters in series in English

# TODO:
# Create a caching mechanism where we can enter a cryptogram and then
# swap letters in the solution map in order to interactively solve a puzzle.

#@respond_to('cache')
# def mycache(message):
#    message.reply("my cache contains: " + cache)

#@respond_to('setcache (.*)')
# def setcache(message,thing):
#    cache = thing
#    message.reply("set cache to: " + cache)

#@respond_to('cachemap')
# def mycachemap(message):
#    message.reply("my cachemap contains: " + cachemap)

#@respond_to('setcachemap (.*)')
# def setcache(message,thing):
#    cachemap = thing
#    message.reply("set cache to: " + cachemap)

