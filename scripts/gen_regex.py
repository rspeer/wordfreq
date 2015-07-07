import argparse
import unicodedata
import chardata

def _emoji_char_class():
    """
    Build a regex for emoji substitution.  First we create a regex character set
    (like "[a-cv-z]") matching characters we consider emoji The final regex
    matches one such character followed by any number of spaces and identical
    characters.
    """
    ranges = []
    for i, c in enumerate(chardata.CHAR_CLASS_STRING):
        if c == '3' and i >= 0x2600 and i != 0xfffd:
            if ranges and i == ranges[-1][1] + 1:
                ranges[-1][1] = i
            else:
                ranges.append([i, i])
    return '[%s]' % ''.join(chr(a) + '-' + chr(b) for a, b in ranges)

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
                start = None
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
    import argparse

    parser = argparse.ArgumentParser(description='Generate a regex matching a function')
    parser.add_argument('acceptor', help='an python function that accepts a single char')
    args = parser.parse_args()
    print(func_to_regex(eval(args.acceptor)))
