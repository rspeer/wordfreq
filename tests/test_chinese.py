from wordfreq import tokenize, word_frequency, zipf_frequency
import pytest


def test_tokens():
    # Let's test on some Chinese text that has unusual combinations of
    # syllables, because it is about an American vice-president.
    #
    # (He was the Chinese Wikipedia's featured article of the day when I
    # wrote this test.)

    hobart = '加勒特·霍巴特'  # Garret Hobart, or "jiā lè tè huò bā tè".

    # He was the sixth American vice president to die in office.
    fact_simplified  = '他是历史上第六位在任期内去世的美国副总统。'
    fact_traditional = '他是歷史上第六位在任期內去世的美國副總統。'

    # His name breaks into five pieces, with the only piece staying together
    # being the one that means 'Bart'. The dot is not included as a token.
    assert tokenize(hobart, 'zh') == ['加', '勒', '特', '霍', '巴特']

    assert tokenize(fact_simplified, 'zh') == [
        # he / is / history / in / #6 / counter for people
        '他', '是',  '历史', '上', '第六', '位',
        # during / term of office / in / die
        '在', '任期', '内', '去世',
        # of / U.S. / deputy / president
        '的', '美国', '副', '总统'
    ]

    # Jieba's original tokenizer knows a lot of names, it seems.
    assert tokenize(hobart, 'zh', external_wordlist=True) == ['加勒特', '霍巴特']

    # We get almost the same tokens from the sentence using Jieba's own
    # wordlist, but it tokenizes "in history" as two words and
    # "sixth person" as one.
    assert tokenize(fact_simplified, 'zh', external_wordlist=True) == [
        # he / is / history / in / sixth person
        '他', '是', '历史', '上', '第六位',
        # during / term of office / in / die
        '在', '任期', '内', '去世',
        # of / U.S. / deputy / president
        '的', '美国', '副', '总统'
    ]

    # Check that Traditional Chinese works at all
    assert word_frequency(fact_traditional, 'zh') > 0

    # You get the same token lengths if you look it up in Traditional Chinese,
    # but the words are different
    simp_tokens = tokenize(fact_simplified, 'zh', include_punctuation=True)
    trad_tokens = tokenize(fact_traditional, 'zh', include_punctuation=True)
    assert ''.join(simp_tokens) == fact_simplified
    assert ''.join(trad_tokens) == fact_traditional
    simp_lengths = [len(token) for token in simp_tokens]
    trad_lengths = [len(token) for token in trad_tokens]
    assert simp_lengths == trad_lengths


def test_combination():
    xiexie_freq = word_frequency('谢谢', 'zh')   # "Thanks"
    assert word_frequency('谢谢谢谢', 'zh') == pytest.approx(xiexie_freq / 20, rel=0.01)


def test_alternate_codes():
    # Tokenization of Chinese works when you use other language codes
    # that are not equal to 'zh'.
    tokens = ['谢谢', '谢谢']

    # Code with a region attached
    assert tokenize('谢谢谢谢', 'zh-CN') == tokens

    # Over-long codes for Chinese
    assert tokenize('谢谢谢谢', 'chi') == tokens
    assert tokenize('谢谢谢谢', 'zho') == tokens

    # Separate codes for Mandarin and Cantonese
    assert tokenize('谢谢谢谢', 'cmn') == tokens
    assert tokenize('谢谢谢谢', 'yue') == tokens


def test_unreasonably_long():
    # This crashed earlier versions of wordfreq due to an overflow in
    # exponentiation. We've now changed the sequence of operations so it
    # will underflow instead.
    lots_of_ls = 'l' * 800
    assert word_frequency(lots_of_ls, 'zh') == 0.
    assert zipf_frequency(lots_of_ls, 'zh') == 0.

