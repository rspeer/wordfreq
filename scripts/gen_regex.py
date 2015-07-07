import unicodedata
from ftfy import chardata
import pathlib
from pkg_resources import resource_filename


DATA_PATH = pathlib.Path(resource_filename('wordfreq', 'data'))


def cache_regex_from_func(filename, func):
    """
    Generates a regex from a function that accepts a single unicode character,
    and caches it in the data path at filename.
    """
    with (DATA_PATH / filename).open(mode='w') as file:
        file.write(func_to_regex(func))


def _emoji_char_class():
    """
    Build a regex for emoji substitution.  We create a regex character set
    (like "[a-cv-z]") matching characters we consider emoji.
    """
    cache_regex_from_func(
        'emoji.txt',
        lambda c:
            chardata.CHAR_CLASS_STRING[ord(c)] == '3' and
            c >= '\u2600' and c != '\ufffd'
    )


def _non_punct_class():
    """
    Builds a regex that matches anything that is not one of the following
    classes:
    - P: punctuation
    - S: symbols
    - Z: separators
    - C: control characters
    This will classify symbols, including emoji, as punctuation; callers that
    want to treat emoji separately should filter them out first.
    """
    cache_regex_from_func(
        'non_punct.txt',
        lambda c: unicodedata.category(c)[0] not in 'PSZC'
    )


def _combining_mark_class():
    """
    Builds a regex that matches anything that is a combining mark
    """
    cache_regex_from_func(
        'combining_mark.txt',
        lambda c: unicodedata.category(c)[0] == 'M'
    )


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
