from wordfreq_builder.word_counts import read_values, write_jieba
import argparse


def handle_counts(filename_in, filename_out):
    freqs, total = read_values(filename_in, cutoff=1e-6)
    write_jieba(freqs, filename_out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename_in', help='name of input wordlist')
    parser.add_argument('filename_out', help='name of output Jieba-compatible wordlist')
    args = parser.parse_args()
    handle_counts(args.filename_in, args.filename_out)
