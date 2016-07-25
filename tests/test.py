from wordfreq import (
    word_frequency, available_languages, cB_to_freq,
    top_n_list, random_words, random_ascii_words, tokenize
)
from nose.tools import (
    eq_, assert_almost_equal, assert_greater, raises
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
    assert_greater(len(avail), 15)

    # Look up a word representing laughter in each language, and make sure
    # it has a non-zero frequency.
    for lang in avail:
        if lang == 'zh' or lang == 'ja':
            text = '笑'
        elif lang == 'ar':
            text = 'ههههه'
        elif lang == 'ca' or lang == 'es':
            text = 'jajaja'
        elif lang in {'de', 'nb', 'sv', 'da'}:
            text = 'haha'
        elif lang == 'pt':
            text = 'kkkk'
        elif lang == 'he':
            text = 'חחח'
        elif lang == 'ru':
            text = 'лол'
        elif lang == 'bg':
            text = 'хаха'
        elif lang == 'ro':
            text = 'ha'
        elif lang == 'el':
            text = 'χαχα'
        else:
            text = 'lol'
        assert_greater(word_frequency(text, lang), 0, lang)

        # Make up a weirdly verbose language code and make sure
        # we still get it
        new_lang_code = '%s-001-x-fake-extension' % lang.upper()
        assert_greater(word_frequency(text, new_lang_code), 0, (text, new_lang_code))


def test_twitter():
    avail = available_languages('twitter')
    assert_greater(len(avail), 14)

    for lang in avail:
        assert_greater(word_frequency('rt', lang, 'twitter'),
                       word_frequency('rt', lang, 'combined'))


def test_minimums():
    eq_(word_frequency('esquivalience', 'en'), 0)
    eq_(word_frequency('esquivalience', 'en', minimum=1e-6), 1e-6)
    eq_(word_frequency('the', 'en', minimum=1), 1)

def test_most_common_words():
    # If something causes the most common words in well-supported languages to
    # change, we should know.

    def get_most_common(lang):
        """
        Return the single most common word in the language.
        """
        return top_n_list(lang, 1)[0]

    eq_(get_most_common('ar'), 'من')
    eq_(get_most_common('de'), 'die')
    eq_(get_most_common('en'), 'the')
    eq_(get_most_common('es'), 'de')
    eq_(get_most_common('fr'), 'de')
    eq_(get_most_common('it'), 'di')
    eq_(get_most_common('ja'), 'の')
    eq_(get_most_common('nl'), 'de')
    eq_(get_most_common('pt'), 'de')
    eq_(get_most_common('ru'), 'в')
    eq_(get_most_common('tr'), 've')
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
    # data
    eq_(tokenize("I don't split at apostrophes, you see.", 'en'),
        ['i', "don't", 'split', 'at', 'apostrophes', 'you', 'see'])

    eq_(tokenize("I don't split at apostrophes, you see.", 'en', include_punctuation=True),
        ['i', "don't", 'split', 'at', 'apostrophes', ',', 'you', 'see', '.'])

    # Certain punctuation does not inherently split a word.
    eq_(tokenize("Anything is possible at zombo.com", 'en'),
        ['anything', 'is', 'possible', 'at', 'zombo.com'])

    # Splits occur after symbols, and at splitting punctuation such as hyphens.
    eq_(tokenize('😂test', 'en'), ['😂', 'test'])

    eq_(tokenize("flip-flop", 'en'), ['flip', 'flop'])

    eq_(tokenize('this text has... punctuation :)', 'en', include_punctuation=True),
        ['this', 'text', 'has', '...', 'punctuation', ':)'])


def test_casefolding():
    eq_(tokenize('WEISS', 'de'), ['weiss'])
    eq_(tokenize('weiß', 'de'), ['weiss'])
    eq_(tokenize('İstanbul', 'tr'), ['istanbul'])
    eq_(tokenize('SIKISINCA', 'tr'), ['sıkısınca'])


def test_phrase_freq():
    ff = word_frequency("flip-flop", 'en')
    assert_greater(ff, 0)
    assert_almost_equal(
        1.0 / ff,
        1.0 / word_frequency('flip', 'en') + 1.0 / word_frequency('flop', 'en')
    )


def test_not_really_random():
    # If your xkcd-style password comes out like this, maybe you shouldn't
    # use it
    eq_(random_words(nwords=4, lang='en', bits_per_word=0),
        'the the the the')

    # This not only tests random_ascii_words, it makes sure we didn't end
    # up with 'eos' as a very common Japanese word
    eq_(random_ascii_words(nwords=4, lang='ja', bits_per_word=0),
        '1 1 1 1')


@raises(ValueError)
def test_not_enough_ascii():
    random_ascii_words(lang='zh', bits_per_word=14)


def test_arabic():
    # Remove tatweels
    eq_(
        tokenize('متــــــــعب', 'ar'),
        ['متعب']
    )

    # Remove combining marks
    eq_(
        tokenize('حَرَكَات', 'ar'),
        ['حركات']
    )

    eq_(
        tokenize('\ufefb', 'ar'),  # An Arabic ligature...
        ['\u0644\u0627']  # ...that is affected by NFKC normalization
    )


def test_ideographic_fallback():
    # Try tokenizing Chinese text as English -- it should remain stuck together.
    eq_(tokenize('中国文字', 'en'), ['中国文字'])

    # When Japanese is tagged with the wrong language, it will be split
    # at script boundaries.
    ja_text = 'ひらがなカタカナromaji'
    eq_(
        tokenize(ja_text, 'en'),
        ['ひらがな', 'カタカナ', 'romaji']
    )

def test_other_languages():
    # Test that we leave Thai letters stuck together. If we had better Thai support,
    # we would actually split this into a three-word phrase.
    eq_(tokenize('การเล่นดนตรี', 'th'), ['การเล่นดนตรี'])
    eq_(tokenize('"การเล่นดนตรี" means "playing music"', 'en'),
        ['การเล่นดนตรี', 'means', 'playing', 'music'])

    # Test Khmer, a script similar to Thai
    eq_(tokenize('សូមស្វាគមន៍', 'km'), ['សូមស្វាគមន៍'])

    # Test Hindi -- tokens split where there are spaces, and not where there aren't
    eq_(tokenize('हिन्दी विक्षनरी', 'hi'), ['हिन्दी', 'विक्षनरी'])

    # Remove vowel points in Hebrew
    eq_(tokenize('דֻּגְמָה', 'he'), ['דגמה'])

    # Deal with commas, cedillas, and I's in Turkish
    eq_(tokenize('kișinin', 'tr'), ['kişinin'])
    eq_(tokenize('KİȘİNİN', 'tr'), ['kişinin'])

    # Deal with cedillas that should be commas-below in Romanian
    eq_(tokenize('acelaşi', 'ro'), ['același'])
    eq_(tokenize('ACELAŞI', 'ro'), ['același'])
