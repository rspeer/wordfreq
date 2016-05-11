from wordfreq_builder.tokenizers import cld2_surface_tokenizer, tokenize_by_language
import argparse


def reddit_tokenizer(text):
    return cld2_surface_tokenizer(text, mode='reddit')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='filename of input file containing one comment per line')
    parser.add_argument('outprefix', help='prefix of output filenames')
    args = parser.parse_args()
    tokenize_by_language(args.filename, args.outprefix, tokenizer=reddit_tokenizer)


if __name__ == '__main__':
    main()
