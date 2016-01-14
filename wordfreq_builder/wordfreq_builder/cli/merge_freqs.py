from wordfreq_builder.word_counts import read_freqs, merge_freqs, write_wordlist
import argparse


def merge_lists(input_names, output_name, cutoff, lang):
    freq_dicts = []

    # Don't use Chinese tokenization while building wordlists, as that would
    # create a circular dependency.
    if lang == 'zh':
        lang = None

    for input_name in input_names:
        freq_dicts.append(read_freqs(input_name, cutoff=cutoff, lang=lang))
    merged = merge_freqs(freq_dicts)
    write_wordlist(merged, output_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', default='combined-freqs.csv',
                        help='filename to write the output to')
    parser.add_argument('-c', '--cutoff', type=int, default=2,
                        help='stop after seeing a count below this')
    parser.add_argument('-l', '--language', default=None,
                        help='language code for which language the words are in')
    parser.add_argument('inputs', nargs='+',
                        help='names of input files to merge')
    args = parser.parse_args()
    merge_lists(args.inputs, args.output, args.cutoff, args.language)

