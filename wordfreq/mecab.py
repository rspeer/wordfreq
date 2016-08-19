from pkg_resources import resource_filename
import MeCab
import unicodedata
import os


# MeCab has fixed-sized buffers for many things, including the dictionary path
MAX_PATH_LENGTH = 58


def find_mecab_dictionary(names):
    """
    Find a MeCab dictionary with a given name. The dictionary has to be
    installed separately -- see wordfreq's README for instructions.
    """
    suggested_pkg = names[0]
    paths = [
        os.path.expanduser('~/.local/lib/mecab/dic'),
        '/var/lib/mecab/dic',
        '/var/local/lib/mecab/dic',
        '/usr/lib/mecab/dic',
        '/usr/local/lib/mecab/dic',
    ]
    full_paths = [os.path.join(path, name) for path in paths for name in names]
    checked_paths = [path for path in full_paths if len(path) <= MAX_PATH_LENGTH]
    for path in checked_paths:
        if os.path.exists(path):
            return path

    error_lines = [
        "Couldn't find the MeCab dictionary named %r." % suggested_pkg,
        "You should download or use your system's package manager to install",
        "the %r package." % suggested_pkg,
        "",
        "We looked in the following locations:"
    ] + ["\t%s" % path for path in checked_paths]

    skipped_paths = [path for path in full_paths if len(path) > MAX_PATH_LENGTH]
    if skipped_paths:
        error_lines += [
            "We had to skip these paths that are too long for MeCab to find:",
        ] + ["\t%s" % path for path in skipped_paths]

    raise OSError('\n'.join(error_lines))


def make_mecab_analyzer(names):
    """
    Get a MeCab analyzer object, given a list of names the dictionary might
    have.
    """
    return MeCab.Tagger('-d %s' % find_mecab_dictionary(names))


# Describe how to get the MeCab analyzers for each language.
MECAB_DICTIONARY_NAMES = {
    'ja': ['mecab-ipadic-utf8', 'ipadic-utf8'],
    'ko': ['mecab-ko-dic', 'ko-dic']
}
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
    if lang not in MECAB_DICTIONARY_NAMES:
        raise ValueError("Can't run MeCab on language %r" % lang)
    if lang not in MECAB_ANALYZERS:
        MECAB_ANALYZERS[lang] = make_mecab_analyzer(MECAB_DICTIONARY_NAMES[lang])

    analyzer = MECAB_ANALYZERS[lang]
    text = unicodedata.normalize('NFKC', text.strip())
    analyzed = analyzer.parse(text)
    if not analyzed:
        return []
    return [line.split('\t')[0]
            for line in analyzed.split('\n')
            if line != '' and line != 'EOS']
