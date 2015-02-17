from wordfreq_builder.word_counts import WordCountBuilder
from wordfreq_builder.tokenizers import rosette_tokenizer, rosette_surface_tokenizer
from pathlib import Path
import argparse


def count_wikipedia(pathname, surface=False):
    path = Path(pathname)
    if surface == True:
        tokenizer = rosette_surface_tokenizer
    else:
        tokenizer = rosette_tokenizer
    builder = WordCountBuilder(tokenizer=tokenizer)
    builder.count_wikipedia(path)
    builder.save_wordlist(path / 'counts.csv')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='directory containing extracted Wikipedia text')
    parser.add_argument('-s', '--surface', action='store_true', help='Use surface text instead of stems')
    args = parser.parse_args()
    count_wikipedia(args.dir, surface=args.surface)

