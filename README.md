#slackbot-puzzle

This includes a number of plugins for the slackbot found at
https://github.com/lins05/slackbot which are useful for solving
ciphers, crypto puzzles, and also for word games.

Special thanks to Mark Santesson for his extremely helpful
[anagram tutorial](http://mostlyhighperformance.blogspot.com/2012/01/generating-anagrams-efficient-and-easy.html)
which is the basis for my anagram and scrabble calls.

##installation

Just drop the folder into your slackbot folder, add 'puzzle-plugins'
to PLUGINS in local_settings.py and away you go.

python3 is required.

##bot commands

###tricky stuff
* anagram: anagram solver for arbitrary number of letters. output /-delimits
  between possible words in a position and space-delimits between letter
  groupings.
* scrabble[5]: find scrabble words given a collection of letters. 
* rotn: show all possible caesar rotations of a string
* matchwildcard: show possible words for a string using ? as a wildcard. e.g.,
  CO?T will give COAT, COST, and others.
* matchword: all words that match a letter pattern, e.g., ABBCDE gives OCCULT
  and a lot more
* matchphrase: find phrases that match a letter pattern, e.g., OFFICE AWARD gives OCCULT
  NINJA and more.
* freq: counts frequencies of letters in a string
* freqsubst[2]: attempts to substitute letters based on English-language 
  frequencies.

###convenience commands
* md5, sha256, ascii2hex, hex2int, ascii2b64, b642ascii, reverse

