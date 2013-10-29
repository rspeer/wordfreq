from __future__ import unicode_literals
from nose.tools import eq_, assert_almost_equal, assert_greater
from wordfreq.query import (word_frequency, average_frequency, wordlist_size,
                            get_wordlists)


def test_freq_examples():
    assert_almost_equal(
        word_frequency('normalization', 'en', 'google-books'),
        1.767e-6, places=9
    )
    assert_almost_equal(
        word_frequency('normalisation', 'fr', 'leeds-internet'),
        4.162e-6, places=9
    )
    assert_greater(
        word_frequency('lol', 'xx', 'twitter'),
        word_frequency('lol', 'en', 'google-books')
    )
    eq_(
        word_frequency('totallyfakeword', 'en', 'multi', -1),
        -1
    )


def _check_normalized_frequencies(wordlist, lang):
    assert_almost_equal(
        average_frequency(wordlist, lang) * wordlist_size(wordlist, lang),
        1.0, places=6
    )


def test_normalized_frequencies():
    for list_info in get_wordlists():
        wordlist = list_info['wordlist']
        lang = list_info['lang']
        yield _check_normalized_frequencies, wordlist, lang
