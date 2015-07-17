""" This file generates a graph of the dependencies for the ninja build.
"""

import sys


def ninja_to_dot():
    def last_component(path):
        return path.split('/')[-1]

    print("digraph G {")
    print('rankdir="LR";')
    for line in sys.stdin:
        line = line.rstrip()
        parts = line.split(' ')
        if parts[0] == 'build':
            # the output file is the first argument; strip off the colon that
            # comes from ninja syntax
            outfile = last_component(parts[1][:-1])
            operation = parts[2]
            infiles = [last_component(part) for part in parts[3:]]
            for infile in infiles:
                if infile == '|':
                    # external dependencies start here; let's not graph those
                    break
                print('"%s" -> "%s" [label="%s"]' % (infile, outfile, operation))
    print("}")


if __name__ == '__main__':
    ninja_to_dot()
