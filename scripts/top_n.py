"""
A quick script to output the top N words (500 for now) in each language.
You can send the output to a file and diff it to see changes between wordfreq
versions.
"""
import wordfreq


N = 500

if __name__ == '__main__':
    for lang in sorted(wordfreq.available_languages()):
        for word in wordfreq.top_n_list(lang, N):
            print('{}\t{}'.format(lang, word))
