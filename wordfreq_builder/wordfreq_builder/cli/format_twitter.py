from wordfreq_builder.tokenizers import retokenize_file
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('in_filename', help='filename of input file containing one tweet per line')
    parser.add_argument('out_filename', help='filename of output file')
    args = parser.parse_args()
    retokenize_file(args.in_filename, args.out_filename)


if __name__ == '__main__':
    main()
