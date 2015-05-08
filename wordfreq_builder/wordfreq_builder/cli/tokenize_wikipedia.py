from wordfreq_builder.tokenizers import rosette_surface_tokenizer, monolingual_tokenize_file
import argparse


def tokenize_wikipedia(in_filename, out_filename, language, proportion):
    monolingual_tokenize_file(
        in_filename, out_filename,
        language=language,
        tokenizer=rosette_surface_tokenizer,
        line_reader=strip_headings,
        sample_proportion=proportion
    )


def strip_headings(text):
    return text.strip().strip('=')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('in_filename', help='filename of input file')
    parser.add_argument('out_filename', help='filename of output file')
    parser.add_argument('language', help='the language code of the text')
    parser.add_argument('-p', '--proportion', help='process 1/n of the lines (default 100)', type=int, default=100)
    args = parser.parse_args()
    tokenize_wikipedia(args.in_filename, args.out_filename, args.language, args.proportion)


if __name__ == '__main__':
    main()
