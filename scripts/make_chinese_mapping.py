"""
Generate a Python file, _chinese_mapping.py, that maps Traditional Chinese
characters to their Simplified Chinese equivalents.

This is meant to be a normalization of text, somewhat like case-folding -- not
an actual translator, a task for which this method would be unsuitable. We
store word frequencies using Simplified Chinese characters so that, in the large
number of cases where a Traditional Chinese word has an obvious Simplified Chinese
mapping, we can get a frequency for it that's the same in Simplified and Traditional
Chinese.

Generating this mapping requires the external Chinese conversion tool OpenCC.
"""
import unicodedata
import itertools
import os
import pprint


def make_hanzi_table(filename):
    with open(filename, 'w', encoding='utf-8') as out:
        for codept in itertools.chain(range(0x3400, 0xa000), range(0xf900, 0xfb00), range(0x20000, 0x30000)):
            char = chr(codept)
            if unicodedata.category(char) != 'Cn':
                print('%5X\t%s' % (codept, char), file=out)


def make_hanzi_converter(table_in, python_out):
    table = {}
    with open(table_in, encoding='utf-8') as infile:
        for line in infile:
            hexcode, char = line.rstrip('\n').split('\t')
            codept = int(hexcode, 16)
            assert len(char) == 1
            if chr(codept) != char:
                table[codept] = char
    with open(python_out, 'w', encoding='utf-8') as outfile:
        print('SIMPLIFIED_MAP = ', end='', file=outfile)
        pprint.pprint(table, stream=outfile)


def build():
    make_hanzi_table('/tmp/han_in.txt')
    os.system('opencc -c zht2zhs.ini < /tmp/han_in.txt > /tmp/han_out.txt')
    make_hanzi_converter('/tmp/han_out.txt', '_chinese_mapping.py')


if __name__ == '__main__':
    build()

