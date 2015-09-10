""" This file generates a graph of the dependencies for the ninja build."""

import sys
import re


def ninja_to_dot():
    def simplified_filename(path):
        component = path.split('/')[-1]
        return re.sub(
            r'[0-9]+-of', 'NN-of',
            re.sub(r'part[0-9]+', 'partNN', component)
        )

    print("digraph G {")
    print('rankdir="LR";')
    seen_edges = set()
    for line in sys.stdin:
        line = line.rstrip()
        if line.startswith('build'):
            # the output file is the first argument; strip off the colon that
            # comes from ninja syntax
            output_text, input_text = line.split(':')
            outfiles = [simplified_filename(part) for part in output_text.split(' ')[1:]]
            inputs = input_text.strip().split(' ')
            infiles = [simplified_filename(part) for part in inputs[1:]]
            operation = inputs[0]
            for infile in infiles:
                if infile == '|':
                    # external dependencies start here; let's not graph those
                    break
                for outfile in outfiles:
                    edge = '"%s" -> "%s" [label="%s"]' % (infile, outfile, operation)
                    if edge not in seen_edges:
                        seen_edges.add(edge)
                        print(edge)
    print("}")


if __name__ == '__main__':
    ninja_to_dot()
