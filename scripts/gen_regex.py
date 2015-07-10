import unicodedata
from ftfy import chardata
import pathlib
from pkg_resources import resource_filename


CATEGORIES = [unicodedata.category(chr(i)) for i in range(0x110000)]
DATA_PATH = pathlib.Path(resource_filename('wordfreq', 'data'))


def func_to_regex(accept):
    """
    Given a function that returns True or False for a numerical codepoint,
    return a regex character class accepting the characters resulting in True.
    Ranges separated only by unassigned characters are merged for efficiency.
    """
    parsing_range = False
    ranges = []

    for codepoint, category in enumerate(CATEGORIES):
        if accept(codepoint):
            if not parsing_range:
                ranges.append([codepoint, codepoint])
                parsing_range = True
            else:
                ranges[-1][1] = codepoint
        elif category != 'Cn':
            parsing_range = False

    return '[%s]' % ''.join('%s-%s' % (chr(r[0]), chr(r[1])) for r in ranges)


def cache_regex_from_func(filename, func):
    """
    Generates a regex from a function that accepts a single unicode character,
    and caches it in the data path at filename.
    """
    with (DATA_PATH / filename).open(mode='w') as file:
        file.write(func_to_regex(func))


def _is_emoji_codepoint(i):
    """
    Report whether a numerical codepoint is (likely) an emoji: a Unicode 'So'
    character (as future-proofed by the ftfy chardata module) but excluding
    symbols like © and ™ below U+2600 and the replacement character U+FFFD.
    """
    return chardata.CHAR_CLASS_STRING[i] == '3' and i >= 0x2600 and i != 0xfffd


def _is_non_punct_codepoint(i):
    """
    Report whether a numerical codepoint is not one of the following classes:
    - P: punctuation
    - S: symbols
    - Z: separators
    - C: control characters
    This will classify symbols, including emoji, as punctuation; users that
    want to accept emoji should add them separately.
    """
    return CATEGORIES[i][0] not in 'PSZC'


def _is_combining_mark_codepoint(i):
    """
    Report whether a numerical codepoint is a combining mark (Unicode 'M').
    """
    return CATEGORIES[i][0] == 'M'


if __name__ == '__main__':
    cache_regex_from_func('emoji.txt', _is_emoji_codepoint)
    cache_regex_from_func('non_punct.txt', _is_non_punct_codepoint)
    cache_regex_from_func('combining_mark.txt', _is_combining_mark_codepoint)
