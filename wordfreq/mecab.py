import MeCab


# Instantiate the MeCab analyzer, which the mecab-python3 interface calls a
# Tagger.
MECAB_ANALYZER = MeCab.Tagger()


def mecab_tokenize(text):
    """
    Use the mecab-python3 package to tokenize the given Japanese text.

    The simplest output from mecab-python3 is the single-string form, which
    contains the same table that the command-line version of MeCab would output.
    We find the tokens in the first column of this table.
    """
    parsed_str = MECAB_ANALYZER.parse(text.strip())
    lines = [line for line in parsed_str.split('\n')
             if line != '' and line != 'EOS']
    tokens = [line.split('\t')[0] for line in lines]
    return tokens
