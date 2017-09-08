"""
A quick script to output the top N words (1000 for now) in each language.
You can send the output to a file and diff it to see changes between wordfreq
versions.
"""
import wordfreq


N = 1000


for lang in sorted(wordfreq.available_languages()):
    for word in wordfreq.top_n_list(lang, 1000):
        print('{}\t{}'.format(lang, word))
