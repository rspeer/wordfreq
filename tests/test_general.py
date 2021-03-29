from wordfreq import (
    word_frequency, available_languages, cB_to_freq,
    top_n_list, random_words, random_ascii_words, tokenize, lossy_tokenize
)
import pytest


def test_freq_examples():
    # Stopwords are most common in the correct language
    assert word_frequency('the', 'en') > word_frequency('de', 'en')
    assert word_frequency('de', 'es') > word_frequency('the', 'es')
    # We get word frequencies from the 'large' list when available
    assert word_frequency('infrequency', 'en') > 0.


def test_languages():
    # Make sure we get all the languages when looking for the default
    # 'best' wordlist
    avail = available_languages()
    assert len(avail) >= 34

    # 'small' covers the same languages, but with some different lists
    avail_small = available_languages('small')
    assert len(avail_small) == len(avail)
    assert avail_small != avail

    # 'combined' is the same as 'small'
    avail_old_name = available_languages('combined')
    assert avail_old_name == avail_small

    # 'large' covers fewer languages
    avail_large = available_languages('large')
    assert len(avail_large) >= 14
    assert len(avail) > len(avail_large)

    # Look up the digit '2' in the main word list for each language
    for lang in avail:
        assert word_frequency('2', lang) > 0

        # Make up a weirdly verbose language code and make sure
        # we still get it
        new_lang_code = '%s-001-x-fake-extension' % lang.upper()
        assert word_frequency('2', new_lang_code) > 0


def test_minimums():
    assert word_frequency('esquivalience', 'en') == 0
    assert word_frequency('esquivalience', 'en', minimum=1e-6) == 1e-6
    assert word_frequency('the', 'en', minimum=1) == 1


def test_most_common_words():
    # If something causes the most common words in well-supported languages to
    # change, we should know.

    def get_most_common(lang):
        """
        Return the single most common word in the language.
        """
        return top_n_list(lang, 1)[0]

    assert get_most_common('ar') == 'في'
    assert get_most_common('bg') == 'на'
    assert get_most_common('bn') == 'না'
    assert get_most_common('ca') == 'de'
    assert get_most_common('cs') == 'a'
    assert get_most_common('da') == 'i'
    assert get_most_common('el') == 'και'
    assert get_most_common('de') == 'die'
    assert get_most_common('en') == 'the'
    assert get_most_common('es') == 'de'
    assert get_most_common('fi') == 'ja'
    assert get_most_common('fil') == 'sa'
    assert get_most_common('fr') == 'de'
    assert get_most_common('gl') == 'de'
    assert get_most_common('he') == 'את'
    assert get_most_common('hi') == 'के'
    assert get_most_common('hu') == 'a'
    assert get_most_common('id') == 'yang'
    assert get_most_common('is') == 'og'
    assert get_most_common('it') == 'di'
    assert get_most_common('ja') == 'の'
    assert get_most_common('ko') == '이'
    assert get_most_common('lt') == 'ir'
    assert get_most_common('lv') == 'un'
    assert get_most_common('mk') == 'на'
    assert get_most_common('ml') == 'ഒരു'
    assert get_most_common('ms') == 'yang'
    assert get_most_common('nb') == 'i'
    assert get_most_common('nl') == 'de'
    assert get_most_common('pl') == 'w'
    assert get_most_common('pt') == 'de'
    assert get_most_common('ro') == 'de'
    assert get_most_common('ru') == 'в'
    assert get_most_common('sh') == 'je'
    assert get_most_common('sk') == 'a'
    assert get_most_common('sl') == 'je'
    assert get_most_common('sv') == 'är'
    assert get_most_common('ta') == 'ஒரு'
    assert get_most_common('tr') == 've'
    assert get_most_common('uk') == 'в'
    assert get_most_common('ur') == 'کے'
    assert get_most_common('vi') == 'là'
    assert get_most_common('zh') == '的'


def test_language_matching():
    freq = word_frequency('的', 'zh')
    assert word_frequency('的', 'zh-TW') == freq
    assert word_frequency('的', 'zh-CN') == freq
    assert word_frequency('的', 'zh-Hant') == freq
    assert word_frequency('的', 'zh-Hans') == freq
    assert word_frequency('的', 'yue-HK') == freq
    assert word_frequency('的', 'cmn') == freq


def test_cB_conversion():
    assert cB_to_freq(0) == 1.
    assert cB_to_freq(-100) == pytest.approx(0.1)
    assert cB_to_freq(-600) == pytest.approx(1e-6)


def test_failed_cB_conversion():
    with pytest.raises(ValueError):
        cB_to_freq(1)


def test_tokenization():
    # We preserve apostrophes within words, so "can't" is a single word in the
    # data
    assert (
        tokenize("I don't split at apostrophes, you see.", 'en')
        == ['i', "don't", 'split', 'at', 'apostrophes', 'you', 'see']
    )

    assert (
        tokenize("I don't split at apostrophes, you see.", 'en', include_punctuation=True)
        == ['i', "don't", 'split', 'at', 'apostrophes', ',', 'you', 'see', '.']
    )

    # Certain punctuation does not inherently split a word.
    assert (
        tokenize("Anything is possible at zombo.com", 'en')
        == ['anything', 'is', 'possible', 'at', 'zombo.com']
    )

    # Splits occur after symbols, and at splitting punctuation such as hyphens.
    assert tokenize('😂test', 'en') == ['😂', 'test']
    assert tokenize("flip-flop", 'en') == ['flip', 'flop']
    assert (
        tokenize('this text has... punctuation :)', 'en', include_punctuation=True)
        == ['this', 'text', 'has', '...', 'punctuation', ':)']
    )

    # Multi-codepoint emoji sequences such as 'medium-skinned woman with headscarf'
    # and 'David Bowie' stay together, because our Unicode segmentation algorithm
    # is up to date
    assert tokenize('emoji test 🧕🏽', 'en') == ['emoji', 'test', '🧕🏽']
    assert (
        tokenize("👨‍🎤 Planet Earth is blue, and there's nothing I can do 🌎🚀", 'en')
        == ['👨‍🎤', 'planet', 'earth', 'is', 'blue', 'and', "there's",
            'nothing', 'i', 'can', 'do', '🌎', '🚀']
    )

    # Water wave, surfer, flag of California (indicates ridiculously complete support
    # for Unicode 10 and Emoji 5.0)
    assert tokenize("Surf's up 🌊🏄🏴󠁵󠁳󠁣󠁡󠁿'",'en') == ["surf's", "up", "🌊", "🏄", "🏴󠁵󠁳󠁣󠁡󠁿"]


def test_casefolding():
    assert tokenize('WEISS', 'de') == ['weiss']
    assert tokenize('weiß', 'de') == ['weiss']
    assert tokenize('İstanbul', 'tr') == ['istanbul']
    assert tokenize('SIKISINCA', 'tr') == ['sıkısınca']


def test_number_smashing():
    assert tokenize('"715 - CRΣΣKS" by Bon Iver', 'en') == ['715', 'crσσks', 'by', 'bon', 'iver']
    assert lossy_tokenize('"715 - CRΣΣKS" by Bon Iver', 'en') == ['000', 'crσσks', 'by', 'bon', 'iver']
    assert (
        lossy_tokenize('"715 - CRΣΣKS" by Bon Iver', 'en', include_punctuation=True)
        == ['"', '000', '-', 'crσσks', '"', 'by', 'bon', 'iver']
    )
    assert lossy_tokenize('1', 'en') == ['1']
    assert lossy_tokenize('3.14', 'en') == ['0.00']
    assert lossy_tokenize('24601', 'en') == ['00000']
    assert word_frequency('24601', 'en') == word_frequency('90210', 'en')


def test_phrase_freq():
    ff = word_frequency("flip-flop", 'en')
    assert ff > 0
    phrase_freq = 1.0 / word_frequency('flip', 'en') + 1.0 / word_frequency('flop', 'en')
    assert 1.0 / ff == pytest.approx(phrase_freq, rel=0.01)


def test_not_really_random():
    # If your xkcd-style password comes out like this, maybe you shouldn't
    # use it
    assert random_words(nwords=4, lang='en', bits_per_word=0) == 'the the the the'

    # This not only tests random_ascii_words, it makes sure we didn't end
    # up with 'eos' as a very common Japanese word
    assert random_ascii_words(nwords=4, lang='ja', bits_per_word=0) == '00 00 00 00'


def test_not_enough_ascii():
    with pytest.raises(ValueError):
        random_ascii_words(lang='zh', bits_per_word=16)


def test_arabic():
    # Remove tatweels
    assert tokenize('متــــــــعب', 'ar') == ['متعب']

    # Remove combining marks
    assert tokenize('حَرَكَات', 'ar') == ['حركات']

    # An Arabic ligature that is affected by NFKC normalization
    assert tokenize('\ufefb', 'ar') == ['\u0644\u0627']


def test_ideographic_fallback():
    # Try tokenizing Chinese text as English -- it should remain stuck together.
    #
    # More complex examples like this, involving the multiple scripts of Japanese,
    # are in test_japanese.py.
    assert tokenize('中国文字', 'en') == ['中国文字']


def test_other_languages():
    # Test that we leave Thai letters stuck together. If we had better Thai support,
    # we would actually split this into a three-word phrase.
    assert tokenize('การเล่นดนตรี', 'th') == ['การเล่นดนตรี']
    assert tokenize('"การเล่นดนตรี" means "playing music"', 'en') == ['การเล่นดนตรี', 'means', 'playing', 'music']

    # Test Khmer, a script similar to Thai
    assert tokenize('សូមស្វាគមន៍', 'km') == ['សូមស្វាគមន៍']

    # Test Hindi -- tokens split where there are spaces, and not where there aren't
    assert tokenize('हिन्दी विक्षनरी', 'hi') == ['हिन्दी', 'विक्षनरी']

    # Remove vowel points in Hebrew
    assert tokenize('דֻּגְמָה', 'he') == ['דגמה']

    # Deal with commas, cedillas, and I's in Turkish
    assert tokenize('kișinin', 'tr') == ['kişinin']
    assert tokenize('KİȘİNİN', 'tr') == ['kişinin']

    # Deal with cedillas that should be commas-below in Romanian
    assert tokenize('acelaşi', 'ro') == ['același']
    assert tokenize('ACELAŞI', 'ro') == ['același']
