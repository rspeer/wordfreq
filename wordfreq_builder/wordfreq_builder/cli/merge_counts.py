from wordfreq_builder.word_counts import read_values, merge_counts, write_wordlist
import argparse


def merge_lists(input_names, output_name, cutoff=0, max_size=1000000):
    count_dicts = []
    for input_name in input_names:
        values, total = read_values(input_name, cutoff=cutoff, max_size=max_size)
        count_dicts.append(values)
    merged = merge_counts(count_dicts)
    write_wordlist(merged, output_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='filename to write the output to', default='combined-counts.csv')
    parser.add_argument('-c', '--cutoff', type=int, default=0, help='minimum count to read from an input file')
    parser.add_argument('-m', '--max-words', type=int, default=1000000, help='maximum number of words to read from each list')
    parser.add_argument('inputs', help='names of input files to merge', nargs='+')
    args = parser.parse_args()
    merge_lists(args.inputs, args.output, cutoff=args.cutoff, max_size=args.max_words)

