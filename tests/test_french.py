from nose.tools import eq_, assert_almost_equal
from wordfreq import tokenize, word_frequency


def test_apostrophes():
    for lang in ('fr', 'ca', 'oc'):
        eq_(tokenize("langues d'oïl", lang),
            ['langues', "d", 'oïl'])
        eq_(tokenize("langues d'oïl", lang, include_punctuation=True),
            ['langues', "d'", 'oïl'])
        eq_(tokenize("l'heure", lang),
            ['l', 'heure'])
        eq_(tokenize("l'heure", lang, include_punctuation=True),
            ["l'", 'heure'])
        eq_(tokenize("L'Hôpital", lang, include_punctuation=True),
            ["l'", 'hôpital'])
        eq_(tokenize("This isn't French", lang),
            ['this', "isn't", 'french'])

