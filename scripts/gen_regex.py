import argparse
import unicodedata
from ftfy import chardata
import pathlib
from pkg_resources import resource_filename


DATA_PATH = pathlib.Path(resource_filename('wordfreq', 'data'))


def _emoji_char_class():
    """
    Build a regex for emoji substitution.  We create a regex character set
    (like "[a-cv-z]") matching characters we consider emoji.
    """
    emoji_file = DATA_PATH / 'emoji.txt'

    def accept(c):
        x = ord(c)
        return chardata.CHAR_CLASS_STRING[x] == '3' and \
                x >= 0x2600 and x != 0xfffd

    with (DATA_PATH / 'emoji.txt').open(mode='w') as file:
        file.write(func_to_regex(accept))


def _non_punct_class():
    """
    Builds a regex that matches anything that is not a one of the following
    classes:
    - P: punctuation
    - S: symbols
    - Z: separators
    - C: control characters
    This will classify symbols, including emoji, as punctuation; callers that
    want to treat emoji separately should filter them out first.
    """
    non_punct_file = DATA_PATH / 'non_punct.txt'

    out = func_to_regex(lambda c: unicodedata.category(c)[0] not in 'PSZC')

    with non_punct_file.open(mode='w') as file:
        file.write(out)


def _combining_mark_class():
    """
    Builds a regex that matches anything that is a combining mark
    """
    combining_mark_file = DATA_PATH / 'combining_mark.txt'
    out = func_to_regex(lambda c: unicodedata.category(c)[0] == 'M')

    with combining_mark_file.open(mode='w') as file:
        file.write(out)


def func_to_regex(accept):
    """
    Converts a function that accepts a single unicode character into a regex.
    Unassigned unicode characters are treated like their neighbors.
    """
    ranges = []
    start = None
    has_accepted = False
    for x in range(0x110000):
        c = chr(x)

        if accept(c):
            has_accepted = True
            if start is None:
                start = c
        elif unicodedata.category(c) == 'Cn':
            if start is None:
                start = c
        elif start is not None:
            if has_accepted:
                ranges.append('-'.join([start, chr(x-1)]))
                has_accepted = False
            start = None
    else:
        if has_accepted and start is not None:
            ranges.append('-'.join([start, chr(x-1)]))

    return '[%s]' % ''.join(ranges)


if __name__ == '__main__':
    _combining_mark_class()
    _non_punct_class()
    _emoji_char_class()
