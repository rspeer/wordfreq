from wordfreq_builder.word_counts import WordCountBuilder
from wordfreq_builder.tokenizers import rosette_tokenizer
from pathlib import Path
import argparse


def count_twitter(pathname, offset=0, nsplit=1):
    path = Path(pathname)
    builder = WordCountBuilder(tokenizer=rosette_tokenizer)
    save_filename = 'twitter-counts-%d.csv' % offset
    save_pathname = path.parent / save_filename
    builder.count_twitter(path, offset, nsplit)
    builder.save_wordlist(save_pathname)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='filename of input file containing one tweet per line')
    parser.add_argument('offset', type=int)
    parser.add_argument('nsplit', type=int)
    args = parser.parse_args()
    count_twitter(args.filename, args.offset, args.nsplit)

