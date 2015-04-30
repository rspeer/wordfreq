from wordfreq_builder.tokenizers import rosette_surface_tokenizer, tokenize_file
import argparse


def tokenize_twitter(in_filename, out_prefix):
    tokenize_file(in_filename, out_prefix,
                  tokenizer=rosette_surface_tokenizer)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='filename of input file containing one tweet per line')
    parser.add_argument('outprefix', help='prefix of output filenames')
    args = parser.parse_args()
    tokenize_twitter(args.filename, args.outprefix)


if __name__ == '__main__':
    main()
