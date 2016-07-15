"""
Count tokens of text in a particular language, taking input from a
tab-separated file whose first column is a language code. Lines in all
languages except the specified one will be skipped.
"""
from wordfreq_builder.word_counts import count_tokens_langtagged, write_wordlist
import argparse


def handle_counts(filename_in, filename_out, lang):
    counts = count_tokens_langtagged(filename_in, lang)
    write_wordlist(counts, filename_out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename_in', help='name of input file containing tokens')
    parser.add_argument('filename_out', help='name of output file')
    parser.add_argument('-l', '--language', help='language tag to filter lines for')
    args = parser.parse_args()
    handle_counts(args.filename_in, args.filename_out, args.language)
