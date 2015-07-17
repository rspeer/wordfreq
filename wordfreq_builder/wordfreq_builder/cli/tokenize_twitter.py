from wordfreq_builder.tokenizers import cld2_surface_tokenizer, tokenize_file
import argparse


def last_tab(line):
    """
    Read lines by keeping only the last tab-separated value.
    """
    return line.split('\t')[-1].strip()


def tokenize_twitter(in_filename, out_prefix):
    tokenize_file(in_filename, out_prefix,
                  tokenizer=cld2_surface_tokenizer,
                  line_reader=last_tab)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='filename of input file containing one tweet per line')
    parser.add_argument('outprefix', help='prefix of output filenames')
    args = parser.parse_args()
    tokenize_twitter(args.filename, args.outprefix)


if __name__ == '__main__':
    main()
