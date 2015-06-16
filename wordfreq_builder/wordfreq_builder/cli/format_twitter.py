import argparse


def retokenize_file(in_filename, out_filename):
    with open(in_filename, encoding='utf-8') as in_file:
        with open(out_filename, 'w', encoding='utf-8') as out_file:
            for line in in_file:
                for token in line.strip().split():
                    print(token, file=out_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('in_filename', help='filename of input file containing one tweet per line')
    parser.add_argument('out_filename', help='filename of output file')
    args = parser.parse_args()
    retokenize_file(args.in_filename, args.out_filename)


if __name__ == '__main__':
    main()
