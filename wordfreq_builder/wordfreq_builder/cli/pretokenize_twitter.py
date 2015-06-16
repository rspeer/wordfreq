from wordfreq_builder.tokenizers import cld2_surface_tokenizer, pretokenize_file
import argparse


def pretokenize_twitter(in_filename, out_prefix):
    pretokenize_file(in_filename, out_prefix,
                     tokenizer=cld2_surface_tokenizer)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='filename of input file containing one tweet per line')
    parser.add_argument('outprefix', help='prefix of output filenames')
    args = parser.parse_args()
    pretokenize_twitter(args.filename, args.outprefix)


if __name__ == '__main__':
    main()
