import argparse
import unicodedata
from ftfy import chardata
import pathlib
from pkg_resources import resource_filename


DATA_PATH = pathlib.Path(resource_filename('wordfreq', 'data'))


def _emoji_char_class():
    """
    Build a regex for emoji substitution.  First we create a regex character set
    (like "[a-cv-z]") matching characters we consider emoji. The final regex
    matches one such character followed by any number of spaces and identical
    characters.
    """
    emoji_file = DATA_PATH / 'emoji.txt'

    ranges = []
    for i, c in enumerate(chardata.CHAR_CLASS_STRING):
        # c represents the character class (3 corresponds to emoji)
        if c == '3' and i >= 0x2600 and i != 0xfffd:
            if ranges and i == ranges[-1][1] + 1:
                ranges[-1][1] = i
            else:
                ranges.append([i, i])
    out = '[%s]' % ''.join(chr(a) + '-' + chr(b) for a, b in ranges)

    with emoji_file.open(mode='w') as file:
        file.write(out)


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
