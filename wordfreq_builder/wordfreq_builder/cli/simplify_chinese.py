from wordfreq.chinese import simplify_chinese
import sys


def main():
    for line in sys.stdin:
        sys.stdout.write(simplify_chinese(line))


if __name__ == '__main__':
    main()
