""" This file generates a graph of the dependencies for the ninja build."""

import sys


def ninja_to_dot():
    def last_component(path):
        return path.split('/')[-1]

    print("digraph G {")
    print('rankdir="LR";')
    for line in sys.stdin:
        line = line.rstrip()
        if line.startswith('build'):
            # the output file is the first argument; strip off the colon that
            # comes from ninja syntax
            output_text, input_text = line.split(':')
            outfiles = [last_component(part) for part in output_text.split(' ')[1:]]
            inputs = input_text.strip().split(' ')
            infiles = [last_component(part) for part in inputs[1:]]
            operation = inputs[0]
            for infile in infiles:
                if infile == '|':
                    # external dependencies start here; let's not graph those
                    break
                for outfile in outfiles:
                    print('"%s" -> "%s" [label="%s"]' % (infile, outfile, operation))
    print("}")


if __name__ == '__main__':
    ninja_to_dot()
