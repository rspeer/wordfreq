from nose.tools import eq_, assert_almost_equal
from wordfreq import tokenize, word_frequency, half_harmonic_mean


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
        word_frequency('おはようございます', 'ja'),
        half_harmonic_mean(
            half_harmonic_mean(ohayou_freq, gozai_freq),
            masu_freq
        )
    )

