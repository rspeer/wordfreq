import MeCab
import unicodedata


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
    text = unicodedata.normalize('NFKC', text.strip())
    return [line.split('\t')[0]
            for line in MECAB_ANALYZER.parse(text).split('\n')
            if line != '' and line != 'EOS']
