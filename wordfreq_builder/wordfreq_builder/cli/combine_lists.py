from wordfreq_builder.word_counts import read_counts, write_counts, merge_counts
from pathlib import Path
import argparse


def merge_lists(input_names, output_name, balance=False):
    count_dicts = []
    for input_name in input_names:
        count_dicts.append(read_counts(Path(input_name)))
    merged = merge_counts(count_dicts, balance=balance)
    write_counts(merged, Path(output_name))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='filename to write the output to', default='combined-counts.csv')
    parser.add_argument('-b', '--balance', action='store_true', help='Automatically balance unequally-sampled word frequencies')
    parser.add_argument('inputs', help='names of input files to merge', nargs='+')
    args = parser.parse_args()
    merge_lists(args.inputs, args.output, balance=args.balance)

