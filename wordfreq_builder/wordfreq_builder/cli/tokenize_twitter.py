from wordfreq_builder.tokenizers import cld2_surface_tokenizer, tokenize_by_language
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='filename of input file containing one tweet per line')
    parser.add_argument('outprefix', help='prefix of output filenames')
    args = parser.parse_args()
    tokenize_by_language(args.filename, args.outprefix, tokenizer=cld2_surface_tokenizer)


if __name__ == '__main__':
    main()
