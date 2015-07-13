from wordfreq_builder.ninja import make_ninja_deps
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('in_filename', help='filename of rules file')
    args = parser.parse_args()

    # Make the complete ninja file and write it to standard out
    make_ninja_deps(args.in_filename)


if __name__ == '__main__':
    main()
