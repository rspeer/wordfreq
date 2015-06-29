from wordfreq import (
    word_frequency, available_languages, cB_to_freq, iter_wordlist,
    top_n_list, random_words, random_ascii_words, tokenize
)
from nose.tools import (
    eq_, assert_almost_equal, assert_greater, assert_less, raises
)


def test_freq_examples():
    # Stopwords are most common in the correct language
    assert_greater(word_frequency('the', 'en'),
                   word_frequency('de', 'en'))

    assert_greater(word_frequency('de', 'es'),
                   word_frequency('the', 'es'))


def test_languages():
    # Make sure the number of available languages doesn't decrease
    avail = available_languages()
    assert_greater(len(avail), 14)

    # Laughter is the universal language
    for lang in avail:
        if lang not in {'zh', 'ja'}:
            # we do not have enough Chinese data
            # Japanese people do not lol
            assert_greater(word_frequency('lol', lang), 0)

            # Make up a weirdly verbose language code and make sure
            # we still get it
            new_lang_code = '%s-001-x-fake-extension' % lang.upper()
            assert_greater(word_frequency('lol', new_lang_code), 0)


def test_defaults():
    eq_(word_frequency('esquivalience', 'en'), 0)
    eq_(word_frequency('esquivalience', 'en', default=1e-6), 1e-6)


def test_most_common_words():
    # If something causes the most common words in well-supported languages to
    # change, we should know.

    def get_most_common(lang):
        """
        Return the single most common word in the language.
        """
        return top_n_list(lang, 1)[0]

    eq_(get_most_common('ar'), 'في')
    eq_(get_most_common('de'), 'die')
    eq_(get_most_common('en'), 'the')
    eq_(get_most_common('es'), 'de')
    eq_(get_most_common('fr'), 'de')
    eq_(get_most_common('it'), 'di')
    eq_(get_most_common('ja'), 'の')
    eq_(get_most_common('nl'), 'de')
    eq_(get_most_common('pt'), 'de')
    eq_(get_most_common('ru'), 'в')
    eq_(get_most_common('zh'), '的')


def test_language_matching():
    freq = word_frequency('的', 'zh')
    eq_(word_frequency('的', 'zh-TW'), freq)
    eq_(word_frequency('的', 'zh-CN'), freq)
    eq_(word_frequency('的', 'zh-Hant'), freq)
    eq_(word_frequency('的', 'zh-Hans'), freq)
    eq_(word_frequency('的', 'yue-HK'), freq)
    eq_(word_frequency('的', 'cmn'), freq)


def test_cB_conversion():
    eq_(cB_to_freq(0), 1.)
    assert_almost_equal(cB_to_freq(-100), 0.1)
    assert_almost_equal(cB_to_freq(-600), 1e-6)


@raises(ValueError)
def test_failed_cB_conversion():
    cB_to_freq(1)


def test_tokenization():
    # We preserve apostrophes within words, so "can't" is a single word in the
    # data, while the fake word "plan't" can't be found.
    eq_(tokenize("can't", 'en'), ["can't"])
    eq_(tokenize("plan't", 'en'), ["plan't"])

    eq_(tokenize('😂test', 'en'), ['😂', 'test'])

    # We do split at other punctuation, causing the word-combining rule to
    # apply.
    eq_(tokenize("can.t", 'en'), ['can', 't'])

def test_phrase_freq():
    plant = word_frequency("plan.t", 'en')
    assert_greater(plant, 0)
    assert_less(plant, word_frequency('plan', 'en'))
    assert_less(plant, word_frequency('t', 'en'))


def test_not_really_random():
    # If your xkcd-style password comes out like this, maybe you shouldn't
    # use it
    eq_(random_words(nwords=4, lang='en', bits_per_word=0),
        'the the the the')

    # This not only tests random_ascii_words, it makes sure we didn't end
    # up with 'eos' as a very common Japanese word
    eq_(random_words(nwords=4, lang='ja', bits_per_word=0),
        'の の の の')


@raises(ValueError)
def test_not_enough_ascii():
    random_ascii_words(lang='zh')
