from wordfreq_builder.word_counts import WordCountBuilder
from wordfreq_builder.tokenizers import rosette_tokenizer
from pathlib import Path
import argparse


def count_wikipedia(pathname):
    path = Path(pathname)
    builder = WordCountBuilder()
    builder.count_wikipedia(path)
    builder.save_wordlist(path / 'counts.csv')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='directory containing extracted Wikipedia text')
    args = parser.parse_args()
    count_wikipedia(args.dir)

