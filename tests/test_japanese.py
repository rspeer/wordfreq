from wordfreq import tokenize, simple_tokenize, word_frequency
import pytest


def test_tokens():
    assert tokenize('おはようございます', 'ja') == ['おはよう', 'ござい', 'ます']


def test_simple_tokenize():
    # When Japanese is run through simple_tokenize -- either because it's
    # tagged with the wrong language, or because we want to pass through
    # Japanese text without getting MeCab involved -- it will be split at
    # boundaries between Japanese and non-Japanese scripts, but all Japanese
    # scripts will be stuck together. Here the switch between hiragana
    # (ひらがな) and katakana (カタカナ) is not a boundary, but the switch
    # between katakana and romaji is.
    #
    # We used to try to infer word boundaries between hiragana and katakana,
    # but this leads to edge cases that are unsolvable without a dictionary.
    ja_text = 'ひらがなカタカナromaji'
    assert simple_tokenize(ja_text) == ['ひらがなカタカナ', 'romaji']
    

    # An example that would be multiple tokens if tokenized as 'ja' via MeCab,
    # but sticks together in simple_tokenize
    assert simple_tokenize('おはようございます') == ['おはようございます']

    # Names that use the weird possessive marker ヶ, which is technically a
    # katakana even though it's being used like a kanji, stay together as one
    # token
    assert simple_tokenize("犬ヶ島") == ["犬ヶ島"]

    # The word in ConceptNet that made me notice that simple_tokenize used
    # to have a problem with the character 々
    assert simple_tokenize("晴々しい") == ["晴々しい"]

    # Explicit word separators are still token boundaries, such as the dot
    # between "toner" and "cartridge" in "toner cartridge"
    assert simple_tokenize("トナー・カートリッジ") == ["トナー", "カートリッジ"]

    # This word has multiple weird characters that aren't quite kanji in it,
    # and is in the dictionary
    assert simple_tokenize("見ヶ〆料") == ["見ヶ〆料"]



def test_combination():
    ohayou_freq = word_frequency('おはよう', 'ja')
    gozai_freq = word_frequency('ござい', 'ja')
    masu_freq = word_frequency('ます', 'ja')

    assert word_frequency('おはようおはよう', 'ja') == pytest.approx(ohayou_freq / 2)
    
    assert (
        1.0 / word_frequency('おはようございます', 'ja') ==
        pytest.approx(1.0 / ohayou_freq + 1.0 / gozai_freq + 1.0 / masu_freq)
    )
    

