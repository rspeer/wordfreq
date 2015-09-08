from wordfreq_builder.word_counts import freqs_to_cBpack
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename_in', help='name of input file containing tokens')
    parser.add_argument('filename_out', help='name of output file')
    args = parser.parse_args()
    freqs_to_cBpack(args.filename_in, args.filename_out)
