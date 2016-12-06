from nose.tools import eq_, assert_almost_equal
from wordfreq import tokenize, word_frequency


def test_apostrophes():
    # Test that we handle apostrophes in French reasonably.
    eq_(tokenize("qu'un", 'fr'), ['qu', 'un'])
    eq_(tokenize("qu'un", 'fr', include_punctuation=True),
        ["qu'", "un"])
    eq_(tokenize("langues d'oïl", 'fr'),
        ['langues', "d", 'oïl'])
    eq_(tokenize("langues d'oïl", 'fr', include_punctuation=True),
        ['langues', "d'", 'oïl'])
    eq_(tokenize("l'heure", 'fr'),
        ['l', 'heure'])
    eq_(tokenize("l'heure", 'fr', include_punctuation=True),
        ["l'", 'heure'])
    eq_(tokenize("L'Hôpital", 'fr', include_punctuation=True),
        ["l'", 'hôpital'])
    eq_(tokenize("This isn't French", 'en'),
        ['this', "isn't", 'french'])


def test_catastrophes():
    # More apostrophes, but this time they're in Catalan, and there's other
    # mid-word punctuation going on too.
    eq_(tokenize("M'acabo d'instal·lar.", 'ca'),
        ['m', 'acabo', 'd', 'instal·lar'])
    eq_(tokenize("M'acabo d'instal·lar.", 'ca', include_punctuation=True),
        ["m'", 'acabo', "d'", 'instal·lar', '.'])
