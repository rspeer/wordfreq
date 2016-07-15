from nose.tools import eq_, assert_almost_equal
from wordfreq import tokenize, word_frequency


def test_tokens():
    eq_(tokenize('감사합니다', 'ko'),
        ['감사', '합니다'])


def test_combination():
    gamsa_freq = word_frequency('감사', 'ko')
    habnida_freq = word_frequency('합니다', 'ko')

    assert_almost_equal(
        word_frequency('감사감사', 'ko'),
        gamsa_freq / 2
    )
    assert_almost_equal(
        1.0 / word_frequency('감사합니다', 'ko'),
        1.0 / gamsa_freq + 1.0 / habnida_freq
    )

