import argparse
import unicodedata

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
