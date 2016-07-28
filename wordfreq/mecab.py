from pkg_resources import resource_filename
import MeCab
import unicodedata


# Instantiate the MeCab analyzers for each language.
MECAB_ANALYZERS = {
    'ja': MeCab.Tagger('-d %s' % resource_filename('wordfreq', 'data/mecab-ja-ipadic')),
    'ko': MeCab.Tagger('-d %s' % resource_filename('wordfreq', 'data/mecab-ko-dic'))
}


def mecab_tokenize(text, lang):
    """
    Use the mecab-python3 package to tokenize the given text. The `lang`
    must be 'ja' for Japanese or 'ko' for Korean.

    The simplest output from mecab-python3 is the single-string form, which
    contains the same table that the command-line version of MeCab would output.
    We find the tokens in the first column of this table.
    """
    if lang not in MECAB_ANALYZERS:
        raise ValueError("Can't run MeCab on language %r" % lang)
    analyzer = MECAB_ANALYZERS[lang]
    text = unicodedata.normalize('NFKC', text.strip())
    analyzed = analyzer.parse(text)
    if not analyzed:
        return []
    return [line.split('\t')[0]
            for line in analyzed.split('\n')
            if line != '' and line != 'EOS']
