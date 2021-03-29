from pkg_resources import resource_filename
import MeCab
import unicodedata
import os


# MeCab has fixed-sized buffers for many things, including the dictionary path
MAX_PATH_LENGTH = 58


def make_mecab_analyzer(lang):
    """
    Get a MeCab analyzer object, given the language code of the language to
    analyze.
    """
    if lang == 'ko':
        import mecab_ko_dic
        return MeCab.Tagger(mecab_ko_dic.MECAB_ARGS)
    elif lang == 'ja':
        import ipadic
        return MeCab.Tagger(ipadic.MECAB_ARGS)
    else:
        raise ValueError("Can't run MeCab on language {lang}".format(lang))


# The constructed analyzers will go in this dictionary.
MECAB_ANALYZERS = {}


def mecab_tokenize(text, lang):
    """
    Use the mecab-python3 package to tokenize the given text. The `lang`
    must be 'ja' for Japanese or 'ko' for Korean.

    The simplest output from mecab-python3 is the single-string form, which
    contains the same table that the command-line version of MeCab would output.
    We find the tokens in the first column of this table.
    """
    if lang not in MECAB_ANALYZERS:
        MECAB_ANALYZERS[lang] = make_mecab_analyzer(lang)

    analyzer = MECAB_ANALYZERS[lang]
    text = unicodedata.normalize('NFKC', text.strip())
    analyzed = analyzer.parse(text)
    if not analyzed:
        return []
    return [line.split('\t')[0]
            for line in analyzed.split('\n')
            if line != '' and line != 'EOS']
