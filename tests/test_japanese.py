from nose.tools import eq_, assert_almost_equal
from wordfreq import tokenize, word_frequency


def test_tokens():
    eq_(tokenize('おはようございます', 'ja'),
        ['おはよう', 'ござい', 'ます'])


def test_combination():
    ohayou_freq = word_frequency('おはよう', 'ja')
    gozai_freq = word_frequency('ござい', 'ja')
    masu_freq = word_frequency('ます', 'ja')

    assert_almost_equal(
        word_frequency('おはようおはよう', 'ja'),
        ohayou_freq / 2
    )
    assert_almost_equal(
        1.0 / word_frequency('おはようございます', 'ja'),
        1.0 / ohayou_freq + 1.0 / gozai_freq + 1.0 / masu_freq
    )

