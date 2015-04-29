from wordfreq_builder.word_counts import WordCountBuilder
from wordfreq_builder.tokenizers import rosette_tokenizer, rosette_surface_tokenizer
from pathlib import Path
import argparse


def count_wikipedia(filename, surface=True):
    path = Path(filename)
    if surface == True:
        tokenizer = rosette_surface_tokenizer
    else:
        tokenizer = rosette_tokenizer
    builder = WordCountBuilder(tokenizer=tokenizer, unique_docs=False)
    builder.count_wikipedia(path)
    builder.save_wordlist(path.parent / 'counts.csv')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='flat text file containing extracted Wikipedia text')
    args = parser.parse_args()
    count_wikipedia(args.filename, surface=True)

